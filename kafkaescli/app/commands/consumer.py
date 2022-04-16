""" App Commands

"""
from dataclasses import dataclass, field
import logging
from typing import AsyncIterator, List, Optional
from uuid import uuid4

from kafkaescli.domain import constants, models
from kafkaescli.domain.models import Config, ConsumerPayload
from kafkaescli.lib.kafka import Consumer, KAFKA_EXCEPTIONS
from kafkaescli.lib.commands import AsyncCommand
from kafkaescli.lib.middleware import MiddlewarePipeline
from kafkaescli.lib.results import as_result
from kafkaescli.lib.webhook import WebhookHandler

logger = logging.getLogger(__name__)


@dataclass
class ConsumeCommand(AsyncCommand):
    config: Config
    topics: List[str]
    group_id: Optional[str] = None
    auto_commit_interval_ms: int = 1000
    auto_offset_reset: str = "latest"
    limit: int = -1
    webhook: Optional[str] = None

    _consumer: Consumer = field(init=False)
    _webhook: WebhookHandler = field(init=False)
    _hook_after_consume: MiddlewarePipeline = field(init=False)

    def __post_init__(self):
        self._hook_after_consume = MiddlewarePipeline(
            self.config.middleware,
            models.MiddlewareHook.AFTER_CONSUME
        )
        self._webhook = WebhookHandler(
            webhook=self.webhook
        )
        self._consumer = Consumer(
            topics=self.topics,
            group_id=self.group_id or f"{constants.APP_PACKAGE}-{uuid4()}",
            enable_auto_commit=False,
            auto_offset_reset=self.auto_offset_reset,
            bootstrap_servers=self.config.bootstrap_servers,
        )


    async def _take_limit(self, iterator: AsyncIterator) -> AsyncIterator:
        num = float('-inf')
        async for value in iterator:
            num += 1
            if self.limit and num >= self.limit:
                break
            yield value

    async def _process_messages(self, messages):
        async with self._webhook.context() as callback:
            async for payload in messages:
                logger.debug("consumed: %r", payload)
                payload = await self._hook_after_consume.execute(payload)
                await callback.execute(payload=payload)
                yield payload

    @as_result(ImportError, *KAFKA_EXCEPTIONS)
    async def execute_async(self) -> AsyncIterator[ConsumerPayload]:
        messages = self._consumer.execute()
        return self._process_messages(self._take_limit(messages))
