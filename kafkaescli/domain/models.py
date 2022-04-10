""" App Models
"""
import base64
from typing import Optional
from uuid import uuid4

from pydantic import UUID4, BaseConfig, BaseModel, fields

from kafkaescli.domain.constants import DEFAULT_BOOTSTRAP_SERVERS
from kafkaescli.domain.types import JSONSerializable


class Model(BaseModel):
    """Models"""

    class Config:
        use_enum_values = True
        extra = "ignore"


class DataModel(Model):
    uuid: UUID4 = fields.Field(default_factory=uuid4)


class Config(Model):
    bootstrap_servers: str = DEFAULT_BOOTSTRAP_SERVERS
    middleware_classes: list[str] = fields.Field(default_factory=list)


class ConfigProfile(Model):
    name: str
    config: Config


class ConfigFile(BaseConfig):
    version: int = 1
    profiles: list[ConfigProfile] = fields.Field(default_factory=list)


class PayloadMetadata(Model):
    topic: str
    partition: int
    offset: int
    timestamp: int

    class Config:
        extra = "allow"


class Payload(Model):
    metadata: PayloadMetadata
    message: JSONSerializable
    key: Optional[JSONSerializable] = fields.Field(default=None)

    class Config:
        json_encoders = {
            bytes: lambda x: base64.b64encode(x).decode("utf-8"),
        }


class ConsumerPayload(Payload):
    """Consumer Payload"""


class ProducerPayload(Payload):
    """Producer Payload"""
