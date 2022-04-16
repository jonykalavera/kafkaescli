""" App Commands
"""
from abc import ABC, abstractmethod
import inspect
from typing import Iterator, TypeVar

from asgiref.sync import async_to_sync

from kafkaescli.lib.results import Result
from kafkaescli.lib.coroutines import async_generator_to_generator


R = TypeVar('R')

class CommandInterface(ABC):
    """Command Interface"""

    @abstractmethod
    def execute(self) -> Result[R, BaseException]:
        """Executes implementation returning a result"""

    @abstractmethod
    async def execute_async(self) -> Result[R, BaseException]:
        """Execute this command asynchronously and return a result."""


class Command(CommandInterface):
    """Command base"""

    async def execute_async(self) -> Result[R, BaseException]:
        return self.execute()


class AsyncCommand(CommandInterface):
    """Async Command base"""

    def _handle_asyncgen(self, r):
        if not inspect.isasyncgen(r):
            return r
        return async_generator_to_generator(r)

    def execute(self) -> Result[R, BaseException]:
        result = async_to_sync(self.execute_async)()
        result.map(self._handle_asyncgen)
        return result
