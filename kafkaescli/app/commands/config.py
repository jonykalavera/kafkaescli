import json
from dataclasses import dataclass
from typing import Optional

from kafkaescli.domain.models import Config, ConfigFile
from kafkaescli.lib.commands import Command
from kafkaescli.lib.results import as_result


@as_result(FileNotFoundError, json.JSONDecodeError)
def _get_config_file_command(config_file_path: Optional[str] = None) -> ConfigFile:
    if not config_file_path:
        return ConfigFile()
    with open(config_file_path) as file:
        data = json.load(file)
        config = ConfigFile.parse_obj(data)
    return config


@dataclass
class GetConfigCommand(Command):
    profile_name: Optional[str] = None
    config_file_path: Optional[str] = None
    overrides: Optional[dict] = None

    def _merge_overrides(self, config: Config) -> Config:
        if self.overrides is None:
            return config
        return Config(**{**config.dict(), **self.overrides})

    def _get_profile_config(self, config_file) -> Config:
        profile_name = self.profile_name or config_file.default_profile
        if profile_name is None:
            return Config()
        for profile in config_file.profiles:
            if profile.name == profile_name:
                return profile.config
        raise ValueError(f'Profile "{profile_name}" not found')

    @as_result(ValueError)
    def execute(self) -> Config:
        config_file = _get_config_file_command(self.config_file_path).unwrap()
        profile_config = self._get_profile_config(config_file=config_file)
        return self._merge_overrides(profile_config)
