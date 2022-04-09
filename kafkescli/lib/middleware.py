import asyncio
from abc import ABCMeta, abstractmethod
from dataclasses import dataclass
from functools import cached_property, lru_cache
from inspect import isabstract
from os import stat
from typing import Any, Callable, ClassVar, Iterator, Optional, TypeVar

from pydantic.utils import import_string

from kafkescli.domain.models import (
    Config,
    ConsumerPayload,
    JSONSerializable,
    Middleware,
)


class MiddlewareInterface(ABCMeta):
    @abstractmethod
    def hook_before_produce(self, message: JSONSerializable) -> JSONSerializable:
        """Hook custom logic to producing a message."""
        return message

    @abstractmethod
    def hook_after_consume(self, payload: ConsumerPayload) -> ConsumerPayload:
        return payload


class Middleware(MiddlewareInterface, ABCMeta):
    def hook_before_produce(self, message: JSONSerializable) -> JSONSerializable:
        """serialize the message to be produced"""
        return message

    def hook_after_consume(self, payload: ConsumerPayload) -> ConsumerPayload:
        return payload


class AsyncMiddleware(Middleware, ABCMeta):
    async def hook_before_produce(self, message: JSONSerializable) -> JSONSerializable:
        """serialize the message to be produced"""
        return message

    async def hook_after_consume(self, payload: ConsumerPayload) -> ConsumerPayload:
        return payload


Bundle = TypeVar("Bundle")


async def _execute_hook_callback(
    callback: Callable[[Bundle], Bundle], bundle: Bundle
) -> Bundle:
    """Middleware hook_method attribute is executed for each middleware in order passing the bundled object."""
    if asyncio.iscoroutinefunction(callback):
        bundle = await callback(bundle)
    bundle = callback(bundle)
    return bundle


@dataclass
class MiddlewarePipeline(MiddlewareInterface):
    """Handles middleware hook execution."""

    middleware_classes: list[str]
    middleware_class_kwargs: Optional[dict[str, Any]] = None

    @cached_property
    def _middleware_layers(self) -> list[Middleware]:
        """Ordered middleware class instances"""
        instances = []
        for doted_path in self.middleware_classes:
            middleware_class = import_string(doted_path)
            instance = middleware_class(**(self.middleware_class_kwargs or {}))
            instances.append(instance)
        return instances

    async def _execute_middleware_hook(
        self, hook_method: str, bundle: Bundle
    ) -> Bundle:
        """Middleware hook_method attribute is executed for each middleware layer passing the bundle object.

        Args:
            hook_method: attribute name.
            bundle: object to transform through the pipeline.
        """
        for instance in self._middleware_layers:
            callback = getattr(instance, hook_method)
            bundle = await _execute_hook_callback(callback=callback, bundle=bundle)
        return bundle

    async def hook_before_produce(self, message: JSONSerializable) -> JSONSerializable:
        """Hook before producing messages

        Args:
            message: message to be transformed.
        Returns:
            message to be produced.
        """
        return await self._execute_middleware_hook("hook_before_produce", message)

    async def hook_after_consume(self, payload: ConsumerPayload) -> ConsumerPayload:
        """Hook after consuming messages

        Args:
            payload: payload to be transformed.
        Returns:
            consumer payload.
        """
        return await self._execute_middleware_hook("hook_after_consume", payload)
