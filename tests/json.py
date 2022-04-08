import json
from datetime import date, datetime
from typing import Union

from pydantic import BaseModel
from pydantic.types import UUID4
from pydantic_factories import ModelFactory


class Person(BaseModel):
    name: str
    hobbies: list[str]
    age: Union[float, int]


class PersonFactory(ModelFactory):
    __model__ = Person


result = PersonFactory.build()


def produce(message):
    if message == "person":
        print("HELLO CALLBACK")
        person = PersonFactory.build()
        message = json.dumps(person.dict())
    return message


async def async_produce(message):
    payload = json.loads(message)
    return json.dumps(payload)


def consume(payload):
    payload["value"] = json.loads(payload["value"])
    print("HELLO CALLBACK")
    return payload


async def async_consume(payload):
    payload["value"] = json.loads(payload["value"])
    print(json.dumps(payload, indent=4))
    return payload
