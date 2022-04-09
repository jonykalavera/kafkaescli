""" App Commands

"""
import logging
from dataclasses import asdict
from typing import TYPE_CHECKING, AsyncIterator, List, Optional

import aiohttp
from aiokafka import AIOKafkaConsumer
from aiokafka.errors import (
    ConsumerStoppedError,
    IllegalOperation,
    IllegalStateError,
    NoOffsetForPartitionError,
    OffsetOutOfRangeError,
    RecordTooLargeError,
    TopicAuthorizationFailedError,
    UnsupportedVersionError,
)
from pydantic.fields import Field

from kafkescli.domain.models import Config, ConsumerPayload
from kafkescli.lib.commands import AsyncCommand
from kafkescli.lib.middleware import MiddlewarePipeline
from kafkescli.lib.results import as_result

if TYPE_CHECKING:
    from aiokafka.structs import ConsumerRecord

logger = logging.getLogger(__name__)


AIOKAFKA_EXCEPTIONS = (
    TopicAuthorizationFailedError,
    OffsetOutOfRangeError,
    ConsumerStoppedError,
    IllegalOperation,
    UnsupportedVersionError,
    IllegalStateError,
    NoOffsetForPartitionError,
    RecordTooLargeError,
)


class ConsumeCommand(AsyncCommand):
    config: Config
    topics: List[str]
    group_id: Optional[str] = Field(default=None)
    auto_commit_interval_ms: int = Field(
        title="Autocommit frequency in milliseconds", default=1000
    )
    auto_offset_reset: str = "earliest"
    metadata: bool = Field(default=True)
    webhook: str = Field(default=None)

    async def consume_messages(self) -> AsyncIterator["ConsumerRecord"]:
        consumer = AIOKafkaConsumer(
            *self.topics,
            group_id=self.group_id,
            enable_auto_commit=False,
            auto_offset_reset=self.auto_offset_reset,
            bootstrap_servers=self.config.bootstrap_servers,
        )
        # Get cluster layout and join group `my-group`
        await consumer.start()
        try:
            # Consume messages
            async for msg in consumer:
                yield msg
                await consumer.commit()
        finally:
            # Will leave consumer group; perform autocommit if enabled.
            await consumer.stop()

    async def _call_webhook(self, session, payload):
        if not self.webhook:
            return
        async with session.post(self.webhook, json=payload, ssl=True) as response:
            text = await response.text()
            logger.info("webhook response", text)

    async def _call_middleware_hook(self, payload: ConsumerPayload) -> ConsumerPayload:
        if self.config.middleware_classes:
            middleware = MiddlewarePipeline(self.config.middleware_classes)
            payload = await middleware.hook_after_consume(payload)
        return payload

    @as_result(ImportError, *AIOKAFKA_EXCEPTIONS)
    async def execute_async(self) -> AsyncIterator["ConsumerRecord"]:
        async with aiohttp.ClientSession(raise_for_status=True) as session:
            async for msg in self.consume_messages():
                payload = ConsumerPayload(
                    **{
                        k: v
                        if not isinstance(v, bytes)
                        else v.decode("utf-8", "ignore")
                        for k, v in asdict(msg).items()
                    }
                )
                logger.debug("consumed: %r", payload)
                payload = await self._call_middleware_hook(payload=payload)
                await self._call_webhook(session=session, payload=payload)
                yield payload
