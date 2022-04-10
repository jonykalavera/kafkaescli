""" Results extension to cover unreleased code in latest version.
"""
import functools
import inspect
import logging
import sys
from asyncio.coroutines import iscoroutinefunction
from typing import Callable, Type, TypeVar

from result import Err, Ok, Result

if sys.version_info[:2] >= (3, 10):
    from typing import ParamSpec
else:
    from typing_extensions import ParamSpec


logger = logging.getLogger(__name__)


P = ParamSpec("P")
R = TypeVar("R")
TBE = TypeVar("TBE", bound=BaseException)


def as_result(
    *exceptions: Type[TBE],
) -> Callable[[Callable[P, R]], Callable[P, Result[R, TBE]]]:
    """
    Make a decorator to turn a function into one that returns a ``Result``.
    Regular return values are turned into ``Ok(return_value)``. Raised
    exceptions of the specified exception type(s) are turned into ``Err(exc)``.
    """
    if not exceptions or not all(
        inspect.isclass(exception) and issubclass(exception, BaseException) for exception in exceptions
    ):
        raise TypeError("as_result() requires one or more exception types")

    def decorator(f: Callable[P, R]) -> Callable[P, Result[R, TBE]]:
        """
        Decorator to turn a function into one that returns a ``Result``.
        """

        def sync_wrapper(*args: P.args, **kwargs: P.kwargs) -> Result[R, TBE]:
            try:
                return Ok(f(*args, **kwargs))
            except exceptions as exc:
                return Err(exc)

        async def async_wrapper(*args: P.args, **kwargs: P.kwargs) -> Result[R, TBE]:
            try:
                returned_value: R = await f(*args, **kwargs)
                return Ok(returned_value)
            except exceptions as exc:
                logger.error("%r", exc)
                return Err(exc)

        return functools.wraps(f)(sync_wrapper if iscoroutinefunction(async_wrapper) else async_wrapper)

    return decorator
