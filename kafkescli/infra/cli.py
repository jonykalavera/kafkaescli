import json
import logging
import sys
import uuid
from functools import partial
from typing import Iterator, Optional

import typer
import uvicorn

from kafkescli.app import commands
from kafkescli.domain import models

app = typer.Typer()
config = models.Config()
logger = logging.getLogger(__name__)


def _log_error_and_exit(error: BaseException):
    """Log error and exit.

    Args:
        err (Exception): exception instance.
    """
    logger.error("%s", error)
    sys.exit(-1)


def _echo_output(metadata, key, messages):
    for msg in messages:
        if metadata:
            output = json.dumps(msg)
        else:
            output = msg.get(key)
        yield output


@app.command()
def consume(
    topics: list[str],
    metadata: bool = typer.Option(False),
    echo: bool = typer.Option(True),
    group_id: str = typer.Option(lambda: f"kafkescli-{uuid.uuid4()}"),
    webhook: Optional[str] = typer.Option(None),
):
    result = commands.ConsumeCommand(
        config=config,
        topics=topics,
        metadata=metadata,
        webhook=webhook,
        group_id=group_id,
    ).execute()
    result.map_err(_log_error_and_exit)
    for msg in result.map(partial(_echo_output, metadata, "value")).unwrap():
        if echo:
            typer.echo(msg)


def _get_lines(file_path="-") -> Iterator[str]:
    if file_path == "-":
        file_descriptor = sys.stdin
    else:
        file_descriptor = open(file_path)
    for line in file_descriptor:
        yield line.strip("\n")


def _get_messages(stdin, file, messages) -> list[str]:
    if stdin:
        messages = list(_get_lines("-"))
    elif file:
        messages = list(_get_lines(file))
    return messages or []


@app.command()
def produce(
    topic: str,
    messages: Optional[list[str]] = typer.Argument(None),
    file: Optional[str] = None,
    stdin: bool = False,
    metadata: bool = False,
    echo: bool = False,
):
    global config
    result = commands.ProduceCommand(
        config=config,
        topic=topic,
        messages=_get_messages(stdin=stdin, file=file, messages=messages),
        callback=callback,
    ).execute()
    result.map_err(_log_error_and_exit)
    for msg in result.map(partial(_echo_output, metadata, "message")).unwrap():
        if echo:
            typer.echo(msg)


@app.command()
def runserver(
    host: str = "localhost",
    port: int = 8000,
    reload: bool = False,
    workers: int = 1,
    log_config: Optional[str] = "INFO",
):
    sys.exit(
        uvicorn.run(
            "kafkescli.infra.web:app",
            host=host,
            port=port,
            reload=reload,
            workers=workers,
            log_config=log_config,
        )
    )


@app.callback()
def main(
    profile: Optional[str] = typer.Option(default="default", envvar="KFK_PROFILE"),
    config_file_path: str = typer.Option(
        default="~/.kafkescli/config", envvar="KFK_CONFIG_FILE_PATH"
    ),
    bootstrap_servers: str = typer.Option(
        default="localhost:9092", envvar="KFK_BOOTSTRAP_SERVERS"
    ),
    middleware_classes: Optional[list[str]] = typer.Option(
        default=None, envvar="KFK_MIDDLEWARE_CLASSES"
    ),
):
    """KafkesCLI"""
    global config
    overrides = dict(
        bootstrap_servers=bootstrap_servers,
        middleware_classes=middleware_classes,
    )
    profile_config = (
        commands.GetConfigCommand(config_file_path=config_file_path, profile=profile)
        .execute()
        .map_err(_log_error_and_exit)
        .unwrap()
    )
    config = models.Config(**{**profile_config.dict(), **overrides})
