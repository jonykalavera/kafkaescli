import asyncio


def handle_asyncgen(ait):
    ait = ait.__aiter__()

    async def get_next():
        try:
            obj = await ait.__anext__()
            return False, obj
        except StopAsyncIteration:
            return True, None

    try:
        loop = asyncio.new_event_loop()
    except RuntimeError:
        loop = asyncio.get_running_loop()

    while True:
        done, obj = loop.run_until_complete(get_next())
        if done:
            break
        yield obj