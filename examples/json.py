import json
from kafkaescli.domain.models import ConsumerPayload
from kafkaescli.domain.types import JSONSerializable

def hook_before_produce(message: JSONSerializable) -> JSONSerializable:
    return json.loads(str(message))


def hook_after_consume(payload: ConsumerPayload) -> ConsumerPayload:
    payload.message = json.loads(str(payload.message))
    return payload

async def hook_before_produce_async(message: JSONSerializable) -> JSONSerializable:
    return json.loads(str(message))


async def hook_after_consume_async(payload: ConsumerPayload) -> ConsumerPayload:
    payload.message = json.loads(str(payload.message))
    return payload