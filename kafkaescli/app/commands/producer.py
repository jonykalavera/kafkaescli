""" Producer Commands
"""
import json
import logging
from functools import cached_property
from typing import AsyncIterator

from kafkaescli.domain.models import Config, ProducerPayload
from kafkaescli.domain.types import JSONSerializable
from kafkaescli.lib import kafka
from kafkaescli.lib.commands import AsyncCommand
from kafkaescli.lib.middleware import MiddlewarePipeline
from kafkaescli.lib.results import as_result

logger = logging.getLogger(__name__)


class ProduceCommand(AsyncCommand):
    config: Config
    topic: str
    messages: list[JSONSerializable]
    partition: int = 1

    def _get_producer_value(self, message: JSONSerializable) -> bytes:
        output = json.dumps(message) if not isinstance(message, (str, bytes)) else message
        output = bytes(output, "utf-8") if not isinstance(output, bytes) else output
        return output

    async def _produce_message(self, message):
        payload = await kafka.produce_message(
            topic=self.topic,
            bootstrap_servers=self.config.bootstrap_servers,
            value=self._get_producer_value(message=message),
            key=None,
        )
        logger.debug("command: %r, output: %r", self.dict(), payload)
        return payload

    @cached_property
    def _middleware(self):
        return MiddlewarePipeline(self.config.middleware_classes)

    async def _call_middleware_hook(self, message: JSONSerializable) -> JSONSerializable:
        if message and self.config.middleware_classes:
            message = await self._middleware.hook_before_produce(message)
        return message

    @as_result(ImportError, RuntimeError, *kafka.KAFKA_EXCEPTIONS)
    async def execute_async(self) -> AsyncIterator[ProducerPayload]:
        for message in self.messages:
            message = await self._call_middleware_hook(message)
            payload = await self._produce_message(message)
            yield payload
