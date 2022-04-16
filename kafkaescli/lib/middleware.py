import asyncio
from dataclasses import dataclass
from functools import cached_property, partial
from typing import Any, Dict, List, Optional, Protocol, TypeVar, Union

from pydantic.utils import import_string

from kafkaescli.domain import models

Bundle = TypeVar("Bundle")


class SyncHookCallback(Protocol):
    def __call__(self, bundle: Bundle, **kwargs) -> Bundle:
        ...


class AsyncHookCallback(Protocol):
    async def __call__(self, bundle: Bundle, **kwargs) -> Bundle:
        ...


HookCallback = Union[SyncHookCallback, AsyncHookCallback]


@dataclass
class MiddlewarePipeline:
    """Handles middleware hook execution."""

    middleware: List[models.Middleware]
    callback: models.MiddlewareHook
    extra_kwargs: Optional[Dict[str, Any]] = None

    def _load_callback(self, middleware: models.Middleware):
        dotted_path = getattr(middleware, self.callback)
        callback = import_string(dotted_path)
        bootstrapped = partial(callback, **(self.extra_kwargs or {}))
        return bootstrapped

    @cached_property
    def _middleware_hook_callbacks(self) -> List[HookCallback]:
        """Ordered middleware class instances"""
        return [self._load_callback(middleware) for middleware in self.middleware]

    async def _execute_hook_callback(self, callback: HookCallback, bundle: Bundle, **kwargs) -> Bundle:
        """Middleware hook_method attribute is executed for each middleware in order passing the bundled object."""
        if asyncio.iscoroutinefunction(callback):
            return await callback(bundle, **kwargs)
        return callback(bundle, **kwargs)

    async def execute(self, bundle: Bundle, **kwargs) -> Bundle:
        """Middleware hook_method attribute is executed for each middleware layer passing the bundle object.

        Args:
            hook_method: attribute name.
            bundle: object to transform through the pipeline.
        """
        for callback in self._middleware_hook_callbacks:
            bundle = await self._execute_hook_callback(callback=callback, bundle=bundle, **kwargs)
        return bundle
