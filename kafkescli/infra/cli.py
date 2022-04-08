import json
import sys
from functools import partial
from typing import Iterator, Optional

import typer
import uvicorn

from kafkescli.app import commands
from kafkescli.domain import models
from kafkescli.infra.utils import log_error_and_exit

app = typer.Typer()
config = models.Config()


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
    metadata: bool = False,
    echo: bool = True,
    callback: Optional[str] = None,
    webhook: Optional[str] = None,
):
    result = commands.ConsumeCommand(
        topics=topics, metadata=metadata, webhook=webhook, callback=callback
    ).execute()
    result.map_err(log_error_and_exit)
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
    callback: Optional[str] = None,
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
    result.map_err(log_error_and_exit)
    for msg in result.map(partial(_echo_output, metadata, "message")).unwrap():
        if echo:
            typer.echo(msg)


@app.command()
def runserver(
    host: str = "localhost",
    port: int = 8000,
    reload: bool = False,
    workers: int = 1,
    log_config: Optional[str] = None,
):
    sys.exit(
        uvicorn.run("kafkescli.infra.web:app", host=host, port=port, reload=reload)
    )


@app.callback()
def main(
    ctx: typer.Context,
    bootstrap_servers: list[str] = typer.Option(
        default=["localhost:9092"], envvar="KFK_BOOTSTRAP_SERVERS"
    ),
):
    """Kafkesque CLI tools"""
    global config
    config = models.Config(bootstrap_servers=bootstrap_servers)
