from typing import List
import pytest
from kafkaescli.domain.models import JSONSerializable

from typer.testing import CliRunner
runner = CliRunner()

from kafkaescli.infra import cli



@pytest.fixture(name="consume_command")
def consumer_command_mock(mocker):
    consumer_command = mocker.patch("kafkaescli.app.commands.ConsumeCommand", autospec=True)
    consumer_command.return_value = consumer_command
    return consumer_command


def test_consume_hello(consume_command, mocker):
    result = runner.invoke(cli.app, ["consume", "hello"])
    consume_command.assert_called_once_with(
        topics=("hello",), config=mocker.ANY, webhook=mocker.ANY, group_id=mocker.ANY, limit=mocker.ANY, auto_offset_reset=mocker.ANY
    )
    assert result.exit_code == 0
    consume_command.execute.assert_called_once_with()


@pytest.fixture(name="produce_command")
def producer_command_mock(mocker):
    producer_command = mocker.patch("kafkaescli.app.commands.ProduceCommand", autospec=True)
    producer_command.return_value = producer_command
    return producer_command


def test_produce_hello_world(produce_command, mocker):
    result = runner.invoke(cli.app, ["produce", "hello", "world"])
    produce_command.assert_called_once_with(
        config=mocker.ANY, topic="hello", values=("world",)
    )
    produce_command.execute.assert_called_once_with()
    assert result.exit_code == 0

@pytest.fixture(name="webserver")
def webserver_mock(mocker):
    webserver = mocker.patch('kafkaescli.infra.cli.uvicorn', autospec=True)
    return webserver


def test_runserver(webserver):
    webserver.run.return_value = 0
    result = runner.invoke(cli.app, ["runserver",])
    webserver.run.assert_called_once_with(
        "kafkaescli.infra.web:app", host='127.0.0.1', port=8000, reload=False, workers=None, log_config=None
    )
    assert result.exit_code == 0
