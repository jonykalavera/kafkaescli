import logging
import sys
from functools import partial
from typing import Iterator, List, Optional

import typer
import uvicorn

from kafkaescli.app import commands
from kafkaescli.domain import constants, models

app = typer.Typer()
config = models.Config()
logger = logging.getLogger(__name__)


def _print_error_and_exit(error: BaseException):
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
    topics: List[str] = typer.Argument(..., envvar="KAFKAESCLI_CONSUMER_TOPICS"),
    metadata: bool = typer.Option(default=False, envvar="KAFKAESCLI_CONSUMER_METADATA"),
    echo: bool = typer.Option(default=True, envvar="KAFKAESCLI_CONSUMER_ECHO"),
    group_id: Optional[str] = typer.Option(default=None, envvar="KAFKAESCLI_CONSUMER_GROUP_ID"),
    webhook: Optional[str] = typer.Option(default=None, envvar="KAFKAESCLI_CONSUMER_WEBHOOK"),
    limit: int = -1,
):
    """ Consume messages from kafka topics.
    """
    result = commands.ConsumeCommand(
        config=config,
        topics=topics,
        webhook=webhook,
        group_id=group_id,
        limit=limit,
    ).execute()
    result.map_err(_print_error_and_exit)
    result.map(partial(_echo_output, metadata=metadata, echo=echo))


def _get_lines(file_path="-") -> Iterator[str]:
    if file_path == "-":
        file_descriptor = sys.stdin
    else:
        file_descriptor = open(file_path)
    for line in file_descriptor:
        yield line.strip("\n")


def _get_messages(stdin, file, messages) -> List[str]:
    if stdin:
        messages = list(_get_lines("-"))
    elif file:
        messages = list(_get_lines(file))
    return messages or []


@app.command()
def produce(
    topic: str = typer.Argument(..., envvar="KAFKAESCLI_PRODUCER_TOPIC"),
    messages: Optional[List[str]] = typer.Argument(None, envvar="KAFKAESCLI_PRODUCER_MESSAGES"),
    file: Optional[str] = typer.Option(None, envvar="KAFKAESCLI_PRODUCER_FILE"),
    stdin: bool = typer.Option(False, envvar="KAFKAESCLI_PRODUCER_STDIN"),
    metadata: bool = typer.Option(True, envvar="KAFKAESCLI_PRODUCER_METADATA"),
    echo: bool = typer.Option(True, envvar="KAFKAESCLI_PRODUCER_ECHO"),
):
    """ Produce messages to kafka.
    """
    global config
    result = commands.ProduceCommand(
        config=config,
        topic=topic,
        messages=_get_messages(stdin=stdin, file=file, messages=messages),
    ).execute()
    result.map_err(_print_error_and_exit)
    result.map(partial(_echo_output, metadata=metadata, key="message", echo=echo))


@app.command()
def runserver(
    host: str = typer.Option("localhost", envvar="KAFKAESCLI_SERVER_HOST"),
    port: int = typer.Option(8000, envvar="KAFKAESCLI_SERVER_PORT"),
    reload: bool = typer.Option(False, envvar="KAFKAESCLI_SERVER_AUTORELOAD"),
    workers: Optional[int] = typer.Option(None, envvar="KAFKAESCLI_SERVER_WORKERS"),
    log_config: Optional[str] = typer.Option(None, envvar="KAFKAESCLI_SEVER_LOG_INFO"),
):
    """ Run webserver interface.
    """
    sys.exit(
        uvicorn.run(
            "kafkaescli.infra.web:app",
            host=host,
            port=port,
            reload=reload,
            workers=workers,
            log_config=log_config
        )
    )


@app.callback()
def main(
    profile: Optional[str] = typer.Option(default=None, envvar="KAFKAESCLI_PROFILE"),
    config_file_path: str = typer.Option(default=None, envvar="KAFKAESCLI_CONFIG_FILE_PATH"),
    bootstrap_servers: str = typer.Option(
        default=constants.DEFAULT_BOOTSTRAP_SERVERS, envvar="KAFKAESCLI_BOOTSTRAP_SERVERS"
    ),
    middleware: Optional[List[str]] = typer.Option(default=None, envvar="KAFKAESCLI_MIDDLEWARE"),
):
    """ A magical kafka command line interface.
    """
    global config
    overrides = dict(
        bootstrap_servers=bootstrap_servers,
        middleware_classes=middleware,
    )
    result = commands.GetConfigCommand(
        config_file_path=config_file_path,
        profile_name=profile,
        overrides=overrides
    ).execute()
    result.map_err(_print_error_and_exit)
    config = result.unwrap()
