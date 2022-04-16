import logging
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from typing import Optional

import aiohttp

from kafkaescli.domain.models import ConsumerPayload

logger = logging.getLogger(__name__)


@dataclass
class WebhookHandler:
    webhook: Optional[str]
    _session: aiohttp.ClientSession = field(init=False)

    @asynccontextmanager
    async def context(self):
        try:
            self._session = aiohttp.ClientSession(raise_for_status=True)
            yield self
        finally:
            await self._session.close()

    async def execute(self, payload: ConsumerPayload) -> None:
        if not self.webhook:
            return
        async with self._session.post(self.webhook, json=payload, ssl=True) as response:
            text = await response.text()
            logger.debug("webhook response", text)
