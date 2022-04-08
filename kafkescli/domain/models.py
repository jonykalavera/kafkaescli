""" App Models
"""
from pydantic import UUID4, BaseConfig, BaseModel


class Model(BaseModel):
    """Models"""

    class Config:
        use_enum_values = True


class DataModel(Model):
    uuid: UUID4


class Config(Model):
    bootstrap_servers: list[str] = ["localhost:9092"]


class Profile(Model):
    name: str
    config: Config


class ConfigFile(BaseConfig):
    default_profile: str = "default"
    profiles: list[Profile] = [Profile(name="default", config=Config())]
