from functools import lru_cache
from typing import AsyncIterator, List, Optional, Union

from fastapi import FastAPI, HTTPException
from starlette.responses import StreamingResponse

from kafkaescli import constants
from kafkaescli.core.consumer.models import ConsumerPayload
from kafkaescli.core.producer.models import ProducerPayload
from kafkaescli.core.shared.models import JSONSerializable
from kafkaescli.infra import containers
from kafkaescli.interface.web import schemas
from kafkaescli.lib.results import Result

app = FastAPI(title=f'{constants.APP_TITLE} API', version=constants.APP_VERSION)
Payload = Union[ConsumerPayload, ProducerPayload]


def respond_with_error(err: BaseException, status_code=500) -> None:
    raise HTTPException(status_code=status_code, detail={"err": str(err)})


async def _stream_values(values: AsyncIterator[Result[Payload, BaseException]]):
    async for value in values:
        yield value.json()
        yield '\n'


@lru_cache
def load_container(profile_name: Optional[str] = None) -> containers.Container:
    container = containers.Container(
        profile_name=profile_name,
    )
    container.init_resources()
    container.wire(modules=[__name__])
    return container


@app.get("/", response_model=schemas.ApiRoot)
def api_root(profile: Optional[str] = None) -> schemas.ApiRoot:
    container = load_container(profile_name=profile)
    return schemas.ApiRoot(
        name=constants.APP_TITLE,
        version=constants.APP_VERSION,
        config=container.config_service().execute().unwrap_or_else(respond_with_error),
    )


@app.post("/produce/{topic}", response_model=ProducerPayload)
async def produce(topic: str, values: List[JSONSerializable], profile: Optional[str] = None) -> StreamingResponse:
    container = load_container(profile_name=profile)
    result = await container.produce_service(topic=topic, values=values).execute_async()
    return StreamingResponse(_stream_values(result.unwrap_or_else(respond_with_error)), media_type="application/json")


@app.post("/consume/{topic}", response_model=ConsumerPayload)
async def consume(
    topic: str,
    limit: int = 1,
    group_id: Optional[str] = None,
    webhook: Optional[str] = None,
    profile: Optional[str] = None,
) -> StreamingResponse:
    container = load_container(profile_name=profile)
    result = await container.consume_service(
        topics=[topic], webhook=webhook, group_id=group_id, limit=limit
    ).execute_async()
    return StreamingResponse(_stream_values(result.unwrap_or_else(respond_with_error)), media_type="application/json")
