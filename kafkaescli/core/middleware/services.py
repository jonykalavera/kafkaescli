import asyncio
from dataclasses import dataclass, field
from functools import cached_property, partial
from types import coroutine
from typing import Any, Dict, List, Optional, Protocol, TypeVar, Union

from pydantic.utils import import_string

from kafkaescli.core.config.services import ConfigService
from kafkaescli.core.middleware.models import Middleware, MiddlewareHook
from kafkaescli.core.shared.services import AsyncService
from kafkaescli.lib.results import as_result

Bundle = TypeVar("Bundle")


class SyncHookCallback(Protocol):
    def __call__(self, bundle: Bundle, **kwargs) -> Bundle:
        ...


class AsyncHookCallback(Protocol):
    async def __call__(self, bundle: Bundle, **kwargs) -> Bundle:
        ...


HookCallback = Union[SyncHookCallback, AsyncHookCallback]


@dataclass
class MiddlewareService(AsyncService):
    config_service: ConfigService
    callback: MiddlewareHook
    extra_kwargs: Optional[Dict[str, Any]] = None

    _middleware: List[Middleware] = field(init=False, default_factory=list)

    def _load_callback(self, middleware: Middleware):
        dotted_path = getattr(middleware, self.callback)
        callback = import_string(dotted_path)
        bootstrapped = partial(callback, **(self.extra_kwargs or {}))
        return bootstrapped

    @cached_property
    def _middleware_hook_callbacks(self) -> List[HookCallback]:
        """Ordered middleware class instances"""
        return [self._load_callback(middleware) for middleware in self._middleware]

    async def _execute_hook_callback(self, callback: HookCallback, bundle: Bundle, **kwargs) -> Bundle:
        """Middleware hook_method attribute is executed for each middleware in order passing the bundled object."""
        if asyncio.iscoroutinefunction(callback):
            return await callback(bundle, **kwargs)
        return callback(bundle, **kwargs)

    async def call(self, bundle: Bundle, **kwargs) -> Bundle:
        for callback in self._middleware_hook_callbacks:
            bundle = await self._execute_hook_callback(callback=callback, bundle=bundle, **kwargs)
        return bundle

    @as_result(ImportError)
    async def execute_async(self) -> 'MiddlewareService':
        """Middleware hook_method attribute is executed for each middleware layer passing the bundle object.

        Args:
            hook_method: attribute name.
            bundle: object to transform through the pipeline.
        """
        config = self.config_service.execute().unwrap_or_throw()
        self._middleware = config.middleware
        return self
