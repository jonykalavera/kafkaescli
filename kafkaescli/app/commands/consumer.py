""" App Commands

"""
import logging
from dataclasses import dataclass, field
from typing import AsyncGenerator, AsyncIterator, List, Optional, Protocol
import uuid

from kafkaescli.domain import constants, models
from kafkaescli.lib.commands import AsyncCommand
from kafkaescli.lib.kafka import KAFKA_EXCEPTIONS
from kafkaescli.lib.results import as_result

logger = logging.getLogger(__name__)


class ConsumerProtocol(Protocol):
    async def execute(self) -> AsyncIterator[models.ConsumerPayload]:
        ...


class WebhookHandlerProtocol(Protocol):
    async def context(self) -> AsyncGenerator['WebhookHandlerProtocol', None]:
        ...

    async def execute(self) -> None:
        ...


class MiddlewarePipelineProtocol(Protocol):
    async def execute(self, bundle: models.ConsumerPayload) -> models.ConsumerPayload:
        ...

@dataclass
class ConsumeCommand(AsyncCommand):
    config: models.Config
    topics: List[str]
    group_id: Optional[str] = None
    auto_commit_interval_ms: int = 1000
    auto_offset_reset: str = "latest"
    limit: int = -1
    webhook: Optional[str] = None

    _consumer: ConsumerProtocol = field(init=False)
    _webhook: WebhookHandlerProtocol = field(init=False)
    _hook_after_consume: MiddlewarePipelineProtocol = field(init=False)

    def __post_init__(self):
        self.group_id = self.group_id or f"{constants.APP_PACKAGE}-{uuid.uuid4()}"

    async def _take_limit(self, iterator: AsyncIterator[models.ConsumerPayload]) -> AsyncIterator[models.ConsumerPayload]:
        num = float('-inf')
        async for value in iterator:
            num += 1
            if self.limit and num >= self.limit:
                break
            yield value

    async def _process_values(self, values: AsyncIterator[models.ConsumerPayload]):
        async with self._webhook.context() as callback:
            async for payload in values:
                logger.debug("consumed: %r", payload)
                payload = await self._hook_after_consume.execute(payload)
                await callback.execute(payload=payload)
                yield payload

    @as_result(ImportError, *KAFKA_EXCEPTIONS)
    async def execute_async(self) -> AsyncIterator[models.ConsumerPayload]:
        values = self._consumer.execute()
        return self._process_values(self._take_limit(values))
