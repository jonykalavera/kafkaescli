""" App Services
"""
import inspect
from abc import ABC, abstractmethod
from typing import (
    AsyncGenerator,
    AsyncIterator,
    Generator,
    Iterator,
    ParamSpec,
    TypeVar,
    Union,
)

from asgiref.sync import async_to_sync

from kafkaescli.lib.coroutines import async_generator_to_generator
from kafkaescli.lib.results import Result

R = TypeVar('R')


class ServiceInterface(ABC):
    """Service Interface"""

    @abstractmethod
    def execute(self) -> Result[R, BaseException]:
        """Executes implementation returning a result"""

    @abstractmethod
    async def execute_async(self) -> Result[R, BaseException]:
        """Execute this service asynchronously and return a result."""


class Service(ServiceInterface):
    """Service base"""

    async def execute_async(self) -> Result[R, BaseException]:
        return self.execute()


class AsyncService(ServiceInterface):
    """Async Service base"""

    def _handle_asyncgen(self, r: AsyncIterator) -> Union[AsyncIterator, Iterator]:
        if not inspect.isasyncgen(r):
            return r
        return async_generator_to_generator(r)

    def execute(self) -> Result[R, BaseException]:
        result = async_to_sync(self.execute_async)()
        result.map(self._handle_asyncgen)
        return result
