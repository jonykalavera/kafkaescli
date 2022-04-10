""" App Commands

"""
import logging
from dataclasses import asdict
from typing import TYPE_CHECKING, AsyncIterator, List, Optional
from uuid import uuid4

import aiohttp
from pydantic.fields import Field

from kafkaescli.domain.models import Config, ConsumerPayload
from kafkaescli.lib import kafka
from kafkaescli.lib.commands import AsyncCommand
from kafkaescli.lib.middleware import MiddlewarePipeline
from kafkaescli.lib.results import as_result

if TYPE_CHECKING:
    from aiokafka.structs import ConsumerRecord

logger = logging.getLogger(__name__)


class ConsumeCommand(AsyncCommand):
    config: Config
    topics: List[str]
    group_id: Optional[str] = Field(default=None)
    auto_commit_interval_ms: int = Field(title="Autocommit frequency in milliseconds", default=1000)
    auto_offset_reset: str = "latest"
    webhook: Optional[str] = Field(default=None)

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

    @as_result(ImportError, *kafka.KAFKA_EXCEPTIONS)
    async def execute_async(self) -> AsyncIterator[ConsumerPayload]:
        async with aiohttp.ClientSession(raise_for_status=True) as session:
            async for payload in kafka.consume_messages(
                topics=self.topics,
                group_id=self.group_id or f"kafkaescli-{uuid4()}",
                enable_auto_commit=False,
                auto_offset_reset=self.auto_offset_reset,
                bootstrap_servers=self.config.bootstrap_servers,
            ):
                logger.debug("consumed: %r", payload)
                payload = await self._call_middleware_hook(payload=payload)
                await self._call_webhook(session=session, payload=payload)
                yield payload
