import json
from kafkaescli.domain.models import ConsumerPayload
from kafkaescli.domain.types import JSONSerializable
from kafkaescli.lib.middleware import Middleware, AsyncMiddleware

class JSONMiddleware(Middleware):
    def hook_before_produce(self, message: JSONSerializable) -> JSONSerializable:
        return json.loads(str(message))


    def hook_after_consume(self, payload: ConsumerPayload) -> ConsumerPayload:
        payload.message = json.loads(str(payload.message))
        return payload


class AsyncJSONMiddleware(AsyncMiddleware):
    async def hook_before_produce(self, message: JSONSerializable) -> JSONSerializable:
        return json.loads(str(message))


    async def hook_after_consume(self, payload: ConsumerPayload) -> ConsumerPayload:
        payload.message = json.loads(str(payload.message))
        return payload