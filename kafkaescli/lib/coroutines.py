import asyncio
from typing import AsyncIterator, Iterator, TypeVar


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

    loop = get_or_create_async_loop()
    while True:
        done, obj = loop.run_until_complete(get_next())
        if done:
            break
        yield obj
