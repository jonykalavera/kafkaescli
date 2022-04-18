import logging
from dataclasses import dataclass, field
from typing import Optional

import aiohttp

from kafkaescli.core.consumer.models import ConsumerPayload
from kafkaescli.core.shared.services import AsyncService
from kafkaescli.lib.results import as_result

logger = logging.getLogger(__name__)


class WebhookHandler(AsyncService):
    _session: aiohttp.ClientSession

    async def __aenter__(self) -> 'WebhookHandler':
        return self

    async def __aexit__(self):
        await self._session.close()

    @as_result(aiohttp.client.ClientError)
    async def send(self, webhook: Optional[str], payload: ConsumerPayload) -> None:
        if not webhook:
            return
        async with self._session.post(webhook, json=payload, ssl=True) as response:
            text = await response.text()
            logger.debug("webhook response", text)

    @as_result(aiohttp.client.ClientError)
    def execute(self):
        self._session = aiohttp.ClientSession(raise_for_status=True)
