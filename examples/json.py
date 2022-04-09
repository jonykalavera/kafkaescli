import json
from datetime import date, datetime
from typing import Union

from pydantic import BaseModel
from pydantic.types import UUID4
from pydantic_factories import ModelFactory


def produce(message):
    message = json.loads(message)
    return json.dumps(message)

async def async_produce(message):
    return produce(message=message)


def consume(payload):
    payload["value"] = json.loads(payload["value"])
    return payload

async def async_consume(payload):
    return consume(message=message)
