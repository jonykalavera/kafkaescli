""" App Models
"""
from functools import cached_property
from typing import Optional

from pydantic import UUID4, BaseConfig, BaseModel, fields
from pydantic.utils import import_string

from kafkescli.domain.types import JSONSerializable


class Model(BaseModel):
    """Models"""

    class Config:
        use_enum_values = True
        extra = "ignore"


class UUIDModel(Model):
    uuid: UUID4


class Config(Model):
    bootstrap_servers: str = "localhost:9092"
    middleware_classes: list[str] = fields.Field(default_factory=list)


class ConfigProfile(Model):
    name: str
    config: Config


class ConfigFile(BaseConfig):
    profiles: list[ConfigProfile] = fields.Field(
        default_factory=lambda: [ConfigProfile(name="default", config=Config())]
    )


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


class ConsumerPayload(Payload):
    """Consumer Payload"""


class ProducerPayload(Payload):
    """Producer Payload"""
