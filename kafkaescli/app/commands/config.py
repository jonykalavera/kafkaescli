from functools import cached_property
import json
from typing import Optional

from pydantic import fields

from kafkaescli.domain.constants import DEFAULT_CONFIG_FILE_PATH
from kafkaescli.domain.models import Config, ConfigFile
from kafkaescli.lib.commands import Command
from kafkaescli.lib.results import as_result


class GetConfigCommand(Command):
    profile_name: Optional[str] = None
    config_file_path: Optional[str] = None

    def get_config_file(self) -> ConfigFile:
        if not self.config_file_path:
            return ConfigFile()
        with open(self.config_file_path) as file:
            config = ConfigFile(*json.load(file))
        return config

    @as_result(ValueError, json.JSONDecodeError, FileNotFoundError)
    def execute(self) -> Config:
        config_file = self.get_config_file()
        profile_name = self.profile_name or config_file.default_profile
        if profile_name is None:
            return Config()
        for profile in config_file.profiles:
            if profile.name == self.profile_name:
                return profile.config
        raise ValueError(f'Profile "{self.profile_name}" not found')
