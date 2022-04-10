import pytest

from kafkaescli.infra import cli


@pytest.fixture(name="consumer_command")
def consumer_command_mock(mocker):
    consumer_command = mocker.patch("kafkaescli.app.commands.ConsumeCommand", autospec=True)
    consumer_command.return_value = consumer_command
    return consumer_command


def test_consume_hello(consumer_command, mocker):
    topics = ["hello"]
    cli.consume(topics=topics)
    consumer_command.assert_called_once_with(topics=topics, config=mocker.ANY, webhook=mocker.ANY, group_id=mocker.ANY)
    consumer_command.execute.assert_called_once_with()
