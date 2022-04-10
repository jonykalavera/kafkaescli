""" App Commands
"""
import asyncio
from abc import ABC, ABCMeta, abstractmethod
from inspect import isasyncgen

from result import Result

from kafkaescli.domain.models import DataModel
from kafkaescli.lib.coroutines import handle_asyncgen


class CommandInterface(ABC):
    """Application Command Interface"""

    @abstractmethod
    def execute(self) -> Result:
        """Executes implementation returning a result"""


class Command(CommandInterface, DataModel):
    """Application Command base"""


class AsyncCommand(Command):
    @property
    def async_loop(self):
        try:
            return asyncio.get_running_loop()
        except RuntimeError:
            return asyncio.new_event_loop()

    def _handle_corrutine(self, coro):
        if isasyncgen(coro):
            value = handle_asyncgen(coro)
        else:
            value = self.async_loop.run_until_complete(coro)
        return value

    def execute(self) -> Result:

        return self.execute_async().map(self._handle_corrutine)

    @abstractmethod
    async def execute_async(self) -> Result:
        """Execute this command asynchronously and return a result."""
