""" Producer Commands
"""
import json
from dataclasses import dataclass, field
from typing import AsyncIterator, List, Optional, Protocol

from kafkaescli.core.config.models import Settings
from kafkaescli.core.middleware.models import Middleware, MiddlewareHook
from kafkaescli.core.producer.models import ProducerPayload
from kafkaescli.core.shared.models import JSONSerializable
from kafkaescli.core.shared.services import AsyncService
from kafkaescli.lib.results import Result, as_result


class ProducerProtocol(Protocol):
    def __init__(self, bootstrap_servers: str):
        ...

    async def execute(
        self, topic: str, value: bytes, key: Optional[bytes] = None, partition=1
    ) -> Result[ProducerPayload, BaseException]:
        ...


class HookBeforeProduceProtocol(Protocol):
    async def call(self, bundle: JSONSerializable) -> Result[JSONSerializable, BaseException]:
        ...

    async def execute_async(self) -> Result['HookBeforeProduceProtocol', BaseException]:
        ...


@dataclass
class ProduceService(AsyncService):
    producer: ProducerProtocol
    hook_before_produce: HookBeforeProduceProtocol
    topic: str
    values: List[JSONSerializable]
    keys: List[Optional[JSONSerializable]] = field(default_factory=list)
    partition: int = 1

    def _producer_bytes(self, value: JSONSerializable) -> bytes:
        output = json.dumps(value) if not isinstance(value, (str, bytes)) else value
        output = bytes(output, "utf-8") if not isinstance(output, bytes) else output
        return output

    async def _produce_value(self, value, key):
        payload = (
            await self.producer.execute(
                topic=self.topic,
                value=self._producer_bytes(value),
                key=self._producer_bytes(key),
                partition=self.partition,
            )
        ).unwrap_or_throw()
        return payload

    @as_result(json.JSONDecodeError)
    async def execute_async(self) -> AsyncIterator[ProducerPayload]:
        keys = self.keys or [None] * len(self.values)
        hook_before_produce = (await self.hook_before_produce.execute_async()).unwrap_or_throw()
        for key, value in zip(keys, self.values):
            value = await hook_before_produce.call(value, key=key)
            payload = await self._produce_value(value, key=key)
            yield payload
