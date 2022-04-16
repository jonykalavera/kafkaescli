from typing import List

from pydantic import BaseModel, fields

from kafkaescli.domain.models import Config, JSONSerializable, ProducerPayload


class APISchema(BaseModel):
    """Common API Schema"""


class ProduceParams(APISchema):
    values: List[JSONSerializable]


class ProduceResponse(APISchema):
    params: ProduceParams
    results: List[ProducerPayload] = fields.Field(default_factory=list)


class ApiRoot(APISchema):
    name: str
    version: str
    config: Config
