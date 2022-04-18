import base64
from typing import Optional

from pydantic import fields

from kafkaescli.core.shared.models import DataModel, JSONSerializable, Model


class PayloadMetadata(Model):
    topic: str
    partition: int
    offset: int
    timestamp: int


class ConsumerPayload(DataModel):
    metadata: PayloadMetadata
    value: JSONSerializable
    key: Optional[JSONSerializable] = fields.Field(default=None)
