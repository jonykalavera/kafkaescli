""" App Commands
"""
import asyncio
from abc import ABC, abstractmethod
from functools import cached_property, partial
from inspect import isasyncgen

from pydantic import BaseModel
from result import Result


class BaseCommand(ABC, BaseModel):
    """ """

    @abstractmethod
    def execute(self) -> Result:
        """ """


class AsyncCommand(ABC, BaseCommand):
    def _handle_asyncgen(self, ait):
        ait = ait.__aiter__()

        async def get_next():
            try:
                obj = await ait.__anext__()
                return False, obj
            except StopAsyncIteration:
                return True, None

        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
        while True:
            done, obj = loop.run_until_complete(get_next())
            if done:
                break
            yield obj

    def _handle_corrutine(self, coro):
        if isasyncgen(coro):
            value = self._handle_asyncgen(coro)
        else:
            value = self._loop.run_until_complete(coro)
        return value

    def execute(self) -> Result:
        try:
            asyncio.get_running_loop()
        except RuntimeError:
            asyncio.new_event_loop()
        return self.execute_async().map(self._handle_corrutine)

    @abstractmethod
    async def execute_async(self) -> Result:
        """Execute this command asynchronously and return a result."""
