import asyncio
from functools import cached_property
from typing import Optional

from pydantic.utils import import_string


class CallbackMixin:
    callback: Optional[str] = None

    @cached_property
    def _callback(self):
        return import_string(self.callback)

    async def _call_callback(self, payload):
        if asyncio.iscoroutinefunction(self._callback):
            return await self._callback(payload)
        return self._callback(payload)
