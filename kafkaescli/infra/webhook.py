import logging
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from typing import AsyncGenerator, Optional

import aiohttp

from kafkaescli.core.consumer.models import ConsumerPayload
from kafkaescli.lib.results import as_result

logger = logging.getLogger(__name__)


@dataclass
class WebhookHandler:
    _session: aiohttp.ClientSession = field(init=False)

    @asynccontextmanager
    async def context(self) -> AsyncGenerator['WebhookHandler', None]:
        try:
            self._session = aiohttp.ClientSession(raise_for_status=True)
            yield self
        finally:
            await self._session.close()

    @as_result(aiohttp.client.ClientError)
    async def execute(self, webhook: Optional[str], payload: ConsumerPayload) -> None:
        if not webhook:
            return
        async with self._session.post(webhook, json=payload, ssl=True) as response:
            text = await response.text()
            logger.debug("webhook response", text)
