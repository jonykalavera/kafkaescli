import pytest

from kafkaescli.infra import cli


@pytest.fixture(name="consume_command")
def consumer_command_mock(mocker):
    consumer_command = mocker.patch("kafkaescli.app.commands.ConsumeCommand", autospec=True)
    consumer_command.return_value = consumer_command
    return consumer_command


def test_consume_hello(consume_command, mocker):
    topics = ["hello"]
    cli.consume(topics=topics)
    consume_command.assert_called_once_with(
        topics=topics, config=mocker.ANY, webhook=mocker.ANY, group_id=mocker.ANY, limit=mocker.ANY, auto_offset_reset=mocker.ANY
    )
    consume_command.execute.assert_called_once_with()


@pytest.fixture(name="produce_command")
def producer_command_mock(mocker):
    producer_command = mocker.patch("kafkaescli.app.commands.ProduceCommand", autospec=True)
    producer_command.return_value = producer_command
    return producer_command


def test_produce_hello_world(produce_command, mocker):
    topic = "hello"
    messages=['world']
    cli.produce(topic=topic, messages=messages)
    produce_command.assert_called_once_with(
        topic=topic, config=mocker.ANY
    )
    produce_command.execute.assert_called_once_with()