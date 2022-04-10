from typing import Any

import pkg_resources
from fastapi import FastAPI, HTTPException

from kafkaescli.app import commands
from kafkaescli.domain import models

app = FastAPI()


@app.get("/")
def read_root():
    return {
        "name": "KafkaesCLI",
        "version": pkg_resources.get_distribution("kafkaescli").version,
    }


async def respond_with_error(err: BaseException):
    raise HTTPException(status_code=500, detail={"err": str(err)})


class ProduceParams(models.Model):
    messages: list[str]


@app.post("/produce/{topic}")
async def produce(topic: str, params: ProduceParams) -> dict[str, list[dict[str, Any]]]:
    result = commands.ProduceCommand(
        config=models.Config(), topic=topic, messages=params.messages
    ).execute_async()
    response = {"messages": list()}
    async for msg in result.unwrap_or(respond_with_error):
        response["messages"].append(msg)
    return response
