""" App Models
"""
import base64
from enum import Enum
from typing import List, Optional, Union
from uuid import uuid4

from pydantic import BaseModel, fields
from pydantic.types import UUID4

from kafkaescli.domain.constants import DEFAULT_BOOTSTRAP_SERVERS, DOT_PATH_RE

# so long as we can send it as json in the end
JSONSerializable = Union[str, bytes, list, dict, tuple, int, float]


class Model(BaseModel):
    """Models"""

    class Config:
        use_enum_values = True
        extra = "ignore"


class DataModel(Model):
    uuid: UUID4 = fields.Field(default_factory=uuid4)


class MiddlewareHook(str, Enum):
    BEFORE_PRODUCE = 'hook_before_produce'
    AFTER_CONSUME = 'hook_after_consume'


class Middleware(Model):
    hook_before_produce: Optional[str] = fields.Field(default=None, regex=DOT_PATH_RE)
    hook_after_consume: Optional[str] = fields.Field(default=None, regex=DOT_PATH_RE)


class Config(Model):
    bootstrap_servers: str = DEFAULT_BOOTSTRAP_SERVERS
    middleware: List[Middleware] = fields.Field(default_factory=list)


class ConfigProfile(Model):
    name: str
    config: Config


class ConfigFile(Model):
    version: int = 1
    default_profile: Optional[str] = None
    profiles: List[ConfigProfile] = fields.Field(default_factory=list)


class PayloadMetadata(Model):
    topic: str
    partition: int
    offset: int
    timestamp: int

    class Config:
        extra = "allow"


class Payload(DataModel):
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
