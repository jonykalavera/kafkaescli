from pydantic import fields

from kafkaescli.domain.models import Model, ProducerPayload
from kafkaescli.domain.types import JSONSerializable


class APISchema(Model):
    """Common API Schema"""


class ProduceParams(APISchema):
    messages: list[JSONSerializable]


class ProduceResponse(APISchema):
    params: ProduceParams
    results: list[ProducerPayload] = fields.Field(default_factory=list)


class ServerRoot(APISchema):
    name: str
    version: str
