from typing import List

from pydantic import BaseModel, fields

from kafkaescli.core.config.models import Settings
from kafkaescli.core.models import JSONSerializable
from kafkaescli.core.producer.models import ProducerPayload


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
    config: Settings
