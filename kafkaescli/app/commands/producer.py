""" Producer Commands
"""
import json
import logging
from dataclasses import dataclass, field
from typing import AsyncIterator, List, Optional

from kafkaescli.domain.models import (
    Config,
    JSONSerializable,
    MiddlewareHook,
    ProducerPayload,
)
from kafkaescli.lib.commands import AsyncCommand
from kafkaescli.lib.kafka import KAFKA_EXCEPTIONS, Producer
from kafkaescli.lib.middleware import MiddlewarePipeline
from kafkaescli.lib.results import as_result

logger = logging.getLogger(__name__)


@dataclass
class ProduceCommand(AsyncCommand):
    config: Config
    topic: str
    values: List[JSONSerializable]
    keys: Optional[List[JSONSerializable]] = None
    partition: int = 1

    _producer: Producer = field(init=False)
    _hook_before_produce: MiddlewarePipeline = field(init=False)

    def __post_init__(self):
        self._hook_before_produce = MiddlewarePipeline(self.config.middleware, MiddlewareHook.AFTER_CONSUME)

    def _producer_bytes(self, value: JSONSerializable) -> bytes:
        output = json.dumps(value) if not isinstance(value, (str, bytes)) else value
        output = bytes(output, "utf-8") if not isinstance(output, bytes) else output
        return output

    async def _produce_value(self, value, key):
        self._producer = Producer(
            topic=self.topic,
            bootstrap_servers=self.config.bootstrap_servers,
            value=self._producer_bytes(value),
            key=self._producer_bytes(key),
        )
        payload = await self._producer.execute()
        logger.debug("command: %r, output: %r", self, payload)
        return payload

    @as_result(ImportError, RuntimeError, *KAFKA_EXCEPTIONS)
    async def execute_async(self) -> AsyncIterator[ProducerPayload]:
        keys = self.keys or [None] * len(self.values)
        for key, value in zip(keys, self.values):
            value = await self._hook_before_produce.execute(value, key=key)
            payload = await self._produce_value(value, key=key)
            yield payload
