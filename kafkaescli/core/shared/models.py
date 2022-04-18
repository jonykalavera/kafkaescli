""" App Models
"""
import base64
from enum import Enum
from typing import List, Optional, Union
from uuid import uuid4

from pydantic import BaseModel, fields
from pydantic.types import UUID4

# so long as we can send it as json in the end
JSONSerializable = Union[str, bytes, list, dict, tuple, int, float]


class Model(BaseModel):
    """Models"""

    class Config:
        use_enum_values = True
        extra = "ignore"


class DataModel(Model):
    uuid: UUID4 = fields.Field(default_factory=uuid4)

    class Config:
        json_encoders = {
            bytes: lambda x: base64.b64encode(x).decode("utf-8"),
        }
