import json
import logging
import sys
import uuid
from functools import partial
from typing import Iterator, Optional

import typer
import uvicorn
from typer.params import Option

from kafkaescli.app import commands
from kafkaescli.domain import constants, models

app = typer.Typer()
config = models.Config()
logger = logging.getLogger(__name__)


def _log_error_and_exit(error: BaseException):
    """Log error and exit.

    Args:
        err (Exception): exception instance.
    """
    typer.secho(f"{error}", fg=typer.colors.BRIGHT_RED)
    sys.exit(-1)


def _echo_output(
    messages: Iterator[models.Payload],
    echo: bool = True,
    metadata: bool = False,
    key: str = "message",
):
    for msg in messages:
        if not echo:
            continue
        if metadata:
            output = msg.json()
        else:
            output = getattr(msg, key)
        typer.echo(output)


@app.command()
def consume(
    topics: list[str] = typer.Argument(..., envvar="KFK_CONSUMER_TOPICS"),
    metadata: bool = typer.Option(default=False, envvar="KFK_CONSUMER_METADATA"),
    echo: bool = typer.Option(default=True, envvar="KFK_CONSUMER_ECHO"),
    group_id: Optional[str] = typer.Option(default=None, envvar="KFK_CONSUMER_GROUP_ID"),
    webhook: Optional[str] = typer.Option(default=None, envvar="KFK_CONSUMER_WEBHOOK"),
):
    result = commands.ConsumeCommand(
        config=config,
        topics=topics,
        webhook=webhook,
        group_id=group_id,
    ).execute()
    result.map_err(_log_error_and_exit)
    result.map(partial(_echo_output, metadata=metadata, key="message", echo=echo))


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
    topic: str = typer.Argument(..., envvar="KFK_PRODUCER_TOPIC"),
    messages: Optional[list[str]] = typer.Argument(None, envvar="KFK_PRODUCER_MESSAGES"),
    file: Optional[str] = typer.Option(None, envvar="KFK_PRODUCER_FILE"),
    stdin: bool = typer.Option(False, envvar="KFK_PRODUCER_STDIN"),
    metadata: bool = typer.Option(True, envvar="KFK_PRODUCER_METADATA"),
    echo: bool = typer.Option(True, envvar="KFK_PRODUCER_ECHO"),
):
    global config
    result = commands.ProduceCommand(
        config=config,
        topic=topic,
        messages=_get_messages(stdin=stdin, file=file, messages=messages),
    ).execute()
    result.map_err(_log_error_and_exit)
    result.map(partial(_echo_output, metadata=metadata, key="message", echo=echo))


@app.command()
def runserver(
    host: str = typer.Option("localhost", envvar="KFK_SERVER_HOST"),
    port: int = typer.Option(8000, envvar="KFK_SERVER_PORT"),
    autoreload: bool = typer.Option(False, envvar="KFK_SERVER_AUTORELOAD"),
    workers: Optional[int] = typer.Option(None, envvar="KFK_SERVER_WORKERS"),
    log_config: Optional[str] = typer.Option("INFO", envvar="KFK_SEVER_LOG_INFO"),
):
    sys.exit(
        uvicorn.run(
            "kafkaescli.infra.web:app",
            host=host,
            port=port,
            reload=autoreload,
            workers=workers,
            log_config=log_config,
        )
    )


@app.callback()
def main(
    profile: Optional[str] = typer.Option(default="default", envvar="KFK_PROFILE"),
    config_file_path: str = typer.Option(default=constants.DEFAULT_CONFIG_FILE_PATH, envvar="KFK_CONFIG_FILE_PATH"),
    bootstrap_servers: str = typer.Option(default=constants.DEFAULT_BOOTSTRAP_SERVERS, envvar="KFK_BOOTSTRAP_SERVERS"),
    middleware: Optional[list[str]] = typer.Option(default=None, envvar="KFK_MIDDLEWARE"),
):
    """Kafkaescli, magical kafka command line interface."""
    global config
    overrides = dict(
        bootstrap_servers=bootstrap_servers,
        middleware_classes=middleware,
    )
    profile_config: models.Config = (
        commands.GetConfigCommand(config_file_path=config_file_path, profile=profile)
        .execute()
        .map_err(_log_error_and_exit)
        .unwrap()
    )
    config = models.Config(**{**profile_config.dict(), **overrides})
