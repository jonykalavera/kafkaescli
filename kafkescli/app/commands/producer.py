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
from kafkescli.domain.models import Config, ProducerPayload
from kafkescli.domain.types import JSONSerializable
from kafkescli.lib.middleware import MiddlewarePipeline
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

    async def _call_hook_before_produce(
        self, message: JSONSerializable
    ) -> JSONSerializable:
        if self.config.middleware_classes:
            middleware = MiddlewarePipeline(self.config.middleware_classes)
            message = await middleware.hook_before_produce(message)
        return message

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
    async def execute_async(self) -> AsyncIterator[ProducerPayload]:
        for message in self.messages:
            message = await self._call_hook_before_produce(message)
            metadata = await self._produce_message(message)
            payload = ProducerPayload(metadata=metadata._asdict(), message=message)
            logger.info("command: %r, output: %r", self.dict(), payload)
            yield payload
