from enum import Enum
from typing import Optional

from pydantic import fields

from kafkaescli.constants import DOT_PATH_RE
from kafkaescli.core.shared.models import Model


class MiddlewareHook(str, Enum):
    BEFORE_PRODUCE = 'hook_before_produce'
    AFTER_CONSUME = 'hook_after_consume'


class Middleware(Model):
    hook_before_produce: Optional[str] = fields.Field(default=None, regex=DOT_PATH_RE)
    hook_after_consume: Optional[str] = fields.Field(default=None, regex=DOT_PATH_RE)
