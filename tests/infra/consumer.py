import pytest

from kafkescli.app.commands import ConsumeCommand


@pytest.fixture(name="consumer")
def setup_tests():
    consumer = patch("kafkescli.app.coomands.consumer.AIOKafkaConsumer", autospec=True)
    return consumer


def test_consume_hello():
    ConsumeCommand(topics="hello")
