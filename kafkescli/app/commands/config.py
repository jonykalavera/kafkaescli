from functools import cached_property
from typing import Optional

from pydantic import fields

from kafkescli.domain.models import Config, ConfigFile
from kafkescli.lib.commands import Command
from kafkescli.lib.results import as_result


class GetConfigCommand(Command):
    profile_name: Optional[str] = None
    config_file_path: str = fields.Field(default="~/.kafkescli/config")

    @cached_property
    def config_file(self):
        # TODO: load config file
        return ConfigFile()

    @as_result(ValueError)
    def execute(self) -> Config:
        if self.profile_name is None:
            return Config()
        for profile in self.config_file.profiles:
            if profile.name == self.profile_name:
                return profile.config
        raise ValueError(f'Profile "{self.profile_name}" not found')
