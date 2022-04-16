from functools import lru_cache
from typing import AsyncIterator, List, Optional

from fastapi import FastAPI, HTTPException
from starlette.responses import StreamingResponse

from kafkaescli.app import commands
from kafkaescli.domain import constants, models
from kafkaescli.infra.web import schemas

app = FastAPI(title=f'{constants.APP_TITLE} API', version=constants.APP_VERSION)


async def _stream_messages(messages: AsyncIterator[models.Payload]):
    async for msg in messages:
        yield msg.json()
        yield '\n'


def respond_with_error(err: BaseException, status_code=500) -> None:
    raise HTTPException(status_code=status_code, detail={"err": str(err)})


@lru_cache
def load_config(profile_name: Optional[str] = None) -> models.Config:
    result = commands.GetConfigCommand(profile_name=profile_name).execute()
    return result.unwrap_or_else(respond_with_error)


@app.get("/", response_model=schemas.ApiRoot)
def api_root(profile: Optional[str] = None) -> schemas.ApiRoot:
    config = load_config(profile_name=profile)
    return schemas.ApiRoot(name=constants.APP_TITLE, version=constants.APP_VERSION, config=config)


@app.post("/produce/{topic}", response_model=models.ProducerPayload)
async def produce(
    topic: str, messages: List[models.JSONSerializable], profile: Optional[str] = None
) -> StreamingResponse:
    config = load_config(profile_name=profile)
    result = await commands.ProduceCommand(config=config, topic=topic, messages=messages).execute_async()
    return StreamingResponse(
        result.handle(_stream_messages, respond_with_error).unwrap(), media_type="application/json"
    )


@app.post("/consume/{topic}", response_model=models.ConsumerPayload)
async def consume(
    topic: str,
    limit: int = 1,
    group_id: Optional[str] = None,
    webhook: Optional[str] = None,
    profile: Optional[str] = None,
) -> StreamingResponse:
    config = load_config(profile_name=profile)
    result = await commands.ConsumeCommand(
        config=config, topics=[topic], webhook=webhook, group_id=group_id, limit=limit
    ).execute_async()
    return StreamingResponse(
        result.handle(_stream_messages, respond_with_error).unwrap(), media_type="application/json"
    )
