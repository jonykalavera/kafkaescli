""" App Commands

"""
import uuid
from dataclasses import dataclass, field
from typing import AsyncContextManager, AsyncIterator, List, Optional, Protocol

from kafkaescli import constants
from kafkaescli.core.consumer.models import ConsumerPayload
from kafkaescli.core.services import AsyncService
from kafkaescli.lib.results import Result


class ConsumerProtocol(Protocol):
    async def execute(
        self,
        topics: List[str],
        group_id: Optional[str] = None,
        enable_auto_commit: bool = False,
        auto_offset_reset: str = 'latest',
        auto_commit_interval_ms: int = 1000,
    ) -> Result[AsyncIterator[ConsumerPayload], BaseException]:
        ...


class WebhookHandlerProtocol(Protocol):
    async def context(self) -> AsyncContextManager['WebhookHandlerProtocol']:
        ...

    async def execute(self, webhook: Optional[str], payload: ConsumerPayload) -> Result[None, BaseException]:
        ...


class HookAfterConsumeProtocol(Protocol):
    async def execute(self, bundle: ConsumerPayload) -> Result[ConsumerPayload, BaseException]:
        ...


@dataclass
class ConsumeService(AsyncService):
    consumer: ConsumerProtocol
    webhook_handler: WebhookHandlerProtocol
    hook_after_consume: HookAfterConsumeProtocol

    topics: List[str]
    group_id: Optional[str] = None
    auto_commit_interval_ms: int = 1000
    auto_offset_reset: str = "latest"
    limit: int = -1
    webhook: Optional[str] = None

    def __post_init__(self):
        self.group_id = self.group_id or f"{constants.APP_PACKAGE}-{uuid.uuid4()}"

    async def _take_limit(self, iterator: AsyncIterator[ConsumerPayload]) -> AsyncIterator[ConsumerPayload]:
        num = -1
        async for value in iterator:
            num += 1
            if self.limit and num >= self.limit:
                break
            yield value

    async def _process_values(self, values: AsyncIterator[ConsumerPayload]):
        hook_after_consume = (await self.hook_after_consume.execute_async()).unwrap()
        async with self.webhook_handler.context() as callback:
            async for payload in values:
                payload = await hook_after_consume.call(payload)
                await callback.execute(self.webhook, payload=payload)
                yield payload

    async def execute_async(self) -> Result[AsyncIterator[ConsumerPayload], BaseException]:
        result = await self.consumer.execute(
            topics=self.topics,
            group_id=self.group_id,
            auto_offset_reset=self.auto_offset_reset,
            auto_commit_interval_ms=self.auto_commit_interval_ms,
        )
        result.map(self._take_limit)
        result.map(self._process_values)
        return result
