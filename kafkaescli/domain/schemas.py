from typing import List
from pydantic import fields

from kafkaescli.domain.models import Config, Model, ProducerPayload
from kafkaescli.domain.types import JSONSerializable


class APISchema(Model):
    """Common API Schema"""


class ProduceParams(APISchema):
    messages: List[JSONSerializable]


class ProduceResponse(APISchema):
    params: ProduceParams
    results: List[ProducerPayload] = fields.Field(default_factory=list)


class ApiRoot(APISchema):
    name: str
    version: str
    config: Config
