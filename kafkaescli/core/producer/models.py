import base64
from typing import Optional

from pydantic import fields

from kafkaescli.core.models import DataModel, JSONSerializable, Model


class PayloadMetadata(Model):
    topic: str
    partition: int
    offset: int
    timestamp: int

    class Config:
        extra = "allow"


class ProducerPayload(DataModel):
    metadata: PayloadMetadata
    value: JSONSerializable
    key: Optional[JSONSerializable] = fields.Field(default=None)

    class Config:
        json_encoders = {
            bytes: lambda x: base64.b64encode(x).decode("utf-8"),
        }
