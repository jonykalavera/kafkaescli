""" Results extension to cover unreleased code in latest version.
"""
import functools
import inspect
import sys
from typing import Callable, Type, TypeVar

from meiga import Result

if sys.version_info[:2] >= (3, 10):
    from typing import ParamSpec
else:
    from typing_extensions import ParamSpec


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

    def _decorator(f: Callable[P, R]) -> Callable[P, Result[R, TBE]]:
        """
        Decorator to turn a function into one that returns a ``Result``.
        """

        @functools.wraps(f)
        def _sync_wrapper(*args: P.args, **kwargs: P.kwargs) -> Result[R, TBE]:
            try:
                return Result(success=f(*args, **kwargs))
            except exceptions as exc:
                return Result(failure=exc)

        @functools.wraps(f)
        async def _async_wrapper(*args: P.args, **kwargs: P.kwargs) -> Result[R, TBE]:
            try:
                return Result(success=(await f(*args, **kwargs)))
            except exceptions as exc:
                return Result(failure=exc)

        @functools.wraps(f)
        async def _asyncgen_wrapper(*args: P.args, **kwargs: P.kwargs) -> Result[R, TBE]:
            """FIXME: does not capture exceptions"""
            try:
                return Result(success=f(*args, **kwargs))
            except exceptions as exc:
                return Result(failure=exc)

        if inspect.iscoroutinefunction(f):
            _wrapper = _async_wrapper
        elif inspect.isasyncgenfunction(f):
            _wrapper = _asyncgen_wrapper
        else:
            _wrapper = _sync_wrapper
        return functools.wraps(f)(_wrapper)

    return _decorator
