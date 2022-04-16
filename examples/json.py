import json
from kafkaescli.domain.models import ConsumerPayload
from kafkaescli.domain.types import JSONSerializable

def hook_before_produce(value: JSONSerializable) -> JSONSerializable:
    return json.loads(str(value))


def hook_after_consume(payload: ConsumerPayload) -> ConsumerPayload:
    payload.value = json.loads(str(payload.value))
    return payload

async def hook_before_produce_async(value: JSONSerializable) -> JSONSerializable:
    return json.loads(str(value))


async def hook_after_consume_async(payload: ConsumerPayload) -> ConsumerPayload:
    payload.value = json.loads(str(payload.value))
    return payload