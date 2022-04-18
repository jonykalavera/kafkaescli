from typing import List, Optional

from pydantic import BaseSettings, fields

from kafkaescli import constants
from kafkaescli.core.middleware.models import Middleware
from kafkaescli.core.shared.models import Model


class Settings(BaseSettings):
    bootstrap_servers: str = fields.Field(
        default=constants.DEFAULT_BOOTSTRAP_SERVERS, env=constants.KAFKAESCLI_BOOTSTRAP_SERVERS
    )
    middleware: List[Middleware] = fields.Field(default_factory=list, env=constants.KAFKAESCLI_MIDDLEWARE)


class ConfigProfile(Model):
    name: str
    config: Settings


class ConfigFile(Model):
    version: int = 1
    default_profile: Optional[str] = None
    profiles: List[ConfigProfile] = fields.Field(default_factory=list)
