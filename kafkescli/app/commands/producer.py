""" App Commands

"""
import asyncio
import logging
from functools import cached_property
from typing import TYPE_CHECKING, AsyncIterator, Optional

from aiokafka import AIOKafkaProducer
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
from pydantic.utils import import_string

from kafkescli.app.commands.base import AsyncCommand
from kafkescli.app.commands.callback import CallbackMixin
from kafkescli.domain.models import Config
from kafkescli.lib.results import as_result

if TYPE_CHECKING:
    from aiokafka.structs import RecordMetadata

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


class ProduceCommand(AsyncCommand):
    config: Config
    topic: str
    messages: list[str]
    partition: int = 1
    callback: Optional[str] = None

    @cached_property
    def _callback(self):
        if not self.callback:
            raise RuntimeError("No callback has been provided")
        return import_string(self.callback)

    async def _call_callback(self, payload):
        if self.callback is None:
            return payload
        if asyncio.iscoroutinefunction(self._callback):
            return await self._callback(payload)
        return self._callback(payload)

    async def _produce_message(self, message) -> "RecordMetadata":
        producer = AIOKafkaProducer(bootstrap_servers=self.config.bootstrap_servers)
        # Get cluster layout and initial topic/partition leadership information
        await producer.start()
        try:
            output = bytes(message, "utf-8") if isinstance(message, str) else message
            meta = await producer.send_and_wait(
                self.topic, output, partition=self.partition
            )
        finally:
            # Wait for all pending messages to be delivered or expire.
            await producer.stop()
        return meta

    @as_result(ImportError, RuntimeError, *AIOKAFKA_EXCEPTIONS)
    async def execute_async(self) -> AsyncIterator[dict]:
        for message in self.messages:
            message = await self._call_callback(message)
            metadata = await self._produce_message(message)
            output = {"metadata": metadata._asdict(), "message": message}
            logger.info("command: %r, output: %r", self.dict(), output)
            yield output
