import pytest
from typer.testing import CliRunner

from kafkaescli.interface import cli

runner = CliRunner()


@pytest.fixture(name="container")
def container_mock(mocker):
    container = mocker.patch("kafkaescli.infra.containers.Container", autospec=True)
    container.init_resources = mocker.Mock()
    container.wire = mocker.Mock()
    container.return_value = container
    return container


def test_consume_hello(container):
    result = runner.invoke(cli.app, ["consume", "hello"])
    container.consume_service.assert_called_once_with(
        topics=("hello",),
        group_id=None,
        auto_offset_reset='latest',
        limit=-1,
        webhook=None,
    )
    container.consume_service.return_value.execute.assert_called_once_with()
    assert result.exit_code == 0


def test_produce_hello_world(container, mocker):
    result = runner.invoke(cli.app, ["produce", "hello", "world"])
    container.produce_service.assert_called_once_with(topic="hello", values=("world",))
    container.produce_service.return_value.execute.assert_called_once_with()
    assert result.exit_code == 0


@pytest.fixture(name="webserver")
def webserver_mock(mocker):
    webserver = mocker.patch('kafkaescli.interface.cli.uvicorn', autospec=True)
    return webserver


def test_runserver(webserver):
    webserver.run.return_value = 0
    result = runner.invoke(
        cli.app,
        [
            "runserver",
        ],
    )
    webserver.run.assert_called_once_with(
        "kafkaescli.interface.web:app",
        host='127.0.0.1',
        port=8000,
        reload=False,
        workers=1,
        log_level='info',
        log_config=None,
    )
    assert result.exit_code == 0
