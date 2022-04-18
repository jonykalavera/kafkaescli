import sys
from typing import Iterator, List, Optional, Union

import typer
import uvicorn

from kafkaescli import constants
from kafkaescli.core.consumer.models import ConsumerPayload
from kafkaescli.core.producer.models import ProducerPayload
from kafkaescli.infra import containers

app = typer.Typer()
Payload = Union[ConsumerPayload, ProducerPayload]


def _print_error_and_exit(error: BaseException):
    """Log error and exit.

    Args:
        err (Exception): exception instance.
    """
    typer.secho(f"{error}", fg=typer.colors.BRIGHT_RED, err=True)
    sys.exit(-1)


def _echo_output(
    values: Iterator[Payload],
    echo: bool = True,
    metadata: bool = False,
    key: str = "value",
):
    for msg in values:
        if not echo:
            continue
        if metadata:
            output = msg.json()
        else:
            output = getattr(msg, key)
        typer.echo(output)


@app.command()
def consume(
    ctx: typer.Context,
    topics: List[str] = typer.Argument(..., envvar=constants.KAFKAESCLI_CONSUMER_TOPICS),
    metadata: bool = typer.Option(default=False, envvar=constants.KAFKAESCLI_CONSUMER_METADATA),
    echo: bool = typer.Option(default=True, envvar=constants.KAFKAESCLI_CONSUMER_ECHO),
    group_id: Optional[str] = typer.Option(default=None, envvar=constants.KAFKAESCLI_CONSUMER_GROUP_ID),
    webhook: Optional[str] = typer.Option(default=None, envvar=constants.KAFKAESCLI_CONSUMER_WEBHOOK),
    auto_offset_reset: str = typer.Option(default='latest'),
    limit: int = typer.Option(default=-1, envvar=constants.KAFKAESCLI_CONSUMER_LIMIT),
):
    """Consume values from kafka topics."""
    result = (
        ctx.meta['core']
        .consume_service(
            topics=topics,
            group_id=group_id,
            auto_offset_reset=auto_offset_reset,
            limit=limit,
            webhook=webhook,
        )
        .execute()
    )
    echo_output = lambda m: _echo_output(m, metadata=metadata, echo=echo)
    result.handle(echo_output, _print_error_and_exit)


def _get_lines(file_path="-") -> Iterator[str]:
    if file_path == "-":
        file_descriptor = sys.stdin
    else:
        file_descriptor = open(file_path)
    for line in file_descriptor:
        yield line.strip("\n")


def _get_values(stdin: bool, file: Optional[str], values: Optional[List[str]] = None) -> List[str]:
    if stdin:
        values = list(_get_lines("-"))
    elif file is not None:
        values = list(_get_lines(file))
    return values or []


@app.command()
def produce(
    ctx: typer.Context,
    topic: str = typer.Argument(..., envvar=constants.KAFKAESCLI_PRODUCER_TOPIC),
    values: Optional[List[str]] = typer.Argument(None, envvar=constants.KAFKAESCLI_PRODUCER_VALUES),
    file: Optional[str] = typer.Option(None, envvar=constants.KAFKAESCLI_PRODUCER_FILE),
    stdin: bool = typer.Option(False, envvar=constants.KAFKAESCLI_PRODUCER_STDIN),
    metadata: bool = typer.Option(True, envvar=constants.KAFKAESCLI_PRODUCER_METADATA),
    echo: bool = typer.Option(True, envvar=constants.KAFKAESCLI_PRODUCER_ECHO),
):
    """Produce values to a kafka topic."""
    global config
    result = (
        ctx.meta['core']
        .produce_service(
            topic=topic,
            values=_get_values(stdin=stdin, file=file, values=values),
        )
        .execute()
    )
    echo_output = lambda x: _echo_output(x, metadata=metadata, key="value", echo=echo)
    result.handle(echo_output, _print_error_and_exit)


@app.command()
def runserver(
    host: str = typer.Option("127.0.0.1", envvar=constants.KAFKAESCLI_SERVER_HOST),
    port: int = typer.Option(8000, envvar=constants.KAFKAESCLI_SERVER_PORT),
    reload: bool = typer.Option(False, envvar=constants.KAFKAESCLI_SERVER_AUTORELOAD),
    workers: Optional[int] = typer.Option(1, envvar=constants.KAFKAESCLI_SERVER_WORKERS),
    log_level: str = typer.Option("info", envvar=constants.KAFKAESCLI_SEVER_LOG_LEVEL),
    log_config: Optional[str] = typer.Option(None, envvar=constants.KAFKAESCLI_SEVER_LOG_CONFIG),
):
    """Run web interface."""
    typer.secho(
        f"{constants.APP_TITLE} API {constants.APP_VERSION}: http://{host}:{port}/docs", fg=typer.colors.BRIGHT_GREEN
    )
    sys.exit(
        uvicorn.run(
            f"{constants.APP_PACKAGE}.interface.web:app",
            host=host,
            port=port,
            reload=reload,
            workers=workers,
            log_level=log_level,
            log_config=log_config,
        )
    )


@app.callback()
def main(
    ctx: typer.Context,
    profile: Optional[str] = typer.Option(default=None, envvar=constants.KAFKAESCLI_PROFILE),
    config_file_path: str = typer.Option(default=None, envvar=constants.KAFKAESCLI_CONFIG_FILE_PATH),
    bootstrap_servers: str = typer.Option(
        default=constants.DEFAULT_BOOTSTRAP_SERVERS, envvar=constants.KAFKAESCLI_BOOTSTRAP_SERVERS
    ),
    middleware: Optional[List[str]] = typer.Option(default=None, envvar=constants.KAFKAESCLI_MIDDLEWARE),
):
    """A magical kafka command line interface."""
    ctx.meta['core'] = containers.Container(
        profile_name=profile,
        config_file_path=config_file_path,
        overrides=dict(
            bootstrap_servers=bootstrap_servers,
            middleware=middleware,
        ),
    )
    ctx.meta['core'].init_resources()
    ctx.meta['core'].wire(modules=[__name__])
