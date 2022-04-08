""" App Commands

"""
import asyncio
import logging
import uuid
from dataclasses import asdict
from functools import cached_property
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
from pydantic.utils import import_string

from kafkescli.app.commands.base import AsyncCommand
from kafkescli.domain.models import Config
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

config = Config(bootstrap_servers=["localhost:9092"])


class ConsumeCommand(AsyncCommand):
    topics: List[str]
    group_id: Optional[str] = Field(default=None)
    auto_offset_reset: str = Field(default="latest")
    metadata: bool = Field(default=True)
    webhook: str = Field(default=None)
    callback: str = Field(default=None)

    async def consume_messages(self) -> AsyncIterator["ConsumerRecord"]:
        consumer = AIOKafkaConsumer(
            *self.topics,
            bootstrap_servers=",".join(config.bootstrap_servers),
            group_id=self.group_id or f"kafkescli-{uuid.uuid4()}",
            auto_offset_reset=self.auto_offset_reset,
        )
        # Get cluster layout and join group `my-group`
        await consumer.start()
        try:
            # Consume messages
            async for msg in consumer:
                yield msg
        finally:
            # Will leave consumer group; perform autocommit if enabled.
            await consumer.stop()

    async def _call_webhook(self, session, payload):
        async with session.post(self.webhook, json=payload, ssl=True) as response:
            text = await response.text()
            logger.info("webhook response", text)

    @cached_property
    def _callback(self):
        return import_string(self.callback)

    async def _call_callback(self, payload):
        if asyncio.iscoroutinefunction(self._callback):
            return await self._callback(payload)
        return self._callback(payload)

    @as_result(ImportError, *AIOKAFKA_EXCEPTIONS)
    async def execute_async(self) -> AsyncIterator["ConsumerRecord"]:
        async with aiohttp.ClientSession(raise_for_status=True) as session:
            async for msg in self.consume_messages():
                payload = {
                    k: v if not isinstance(v, bytes) else v.decode("utf-8", "ignore")
                    for k, v in asdict(msg).items()
                }
                logger.debug("consumed: %r", payload)
                if self.callback:
                    payload = await self._call_callback(payload=asdict(msg))
                if self.webhook:
                    await self._call_webhook(session=session, payload=payload)
                yield payload
