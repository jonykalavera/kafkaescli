from typing import Any, Optional

import pkg_resources
from fastapi import FastAPI, HTTPException

from kafkaescli.app import commands
from kafkaescli.domain import models, schemas

app = FastAPI()


@app.get("/")
def read_root() -> schemas.ServerRoot:
    return schemas.ServerRoot(name="KafkaesCLI", version=pkg_resources.get_distribution("kafkaescli").version)


async def respond_with_error(err: BaseException):
    raise HTTPException(status_code=500, detail={"err": str(err)})


@app.post("/produce/{topic}")
async def produce(topic: str, params: schemas.ProduceParams, profile: Optional[str] = None) -> list[models.ProducerPayload]:
    config = commands.GetConfigCommand(profile_name=profile).execute().map_err(respond_with_error).unwrap()
    result = commands.ProduceCommand(config=config, topic=topic, messages=params.messages).execute_async()
    result.map_err(respond_with_error)
    results = []
    async for msg in result.unwrap():
        results.append(msg)
    return results
