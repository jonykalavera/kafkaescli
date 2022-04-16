import asyncio
from typing import AsyncIterator, Awaitable, Iterator, Literal, TypeVar, Union


def get_or_create_async_loop():
    try:
        return asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.new_event_loop()


I = TypeVar("I")


def async_generator_to_generator(ait: AsyncIterator[I]) -> Iterator[I]:
    ait = ait.__aiter__()

    async def get_next():
        try:
            obj = await ait.__anext__()
            return False, obj
        except StopAsyncIteration:
            return True, None

    while True:
        done, obj = get_or_create_async_loop().run_until_complete(get_next())
        if done:
            break
        yield obj
