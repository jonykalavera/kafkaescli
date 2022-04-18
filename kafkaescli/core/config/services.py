import json
from dataclasses import dataclass
from typing import Optional

from kafkaescli.core.config.models import ConfigFile, Settings
from kafkaescli.core.shared.services import Service
from kafkaescli.lib.results import as_result


@dataclass
class ConfigFileService(Service):
    config_file_path: Optional[str] = None

    @as_result(FileNotFoundError, json.JSONDecodeError)
    def execute(self) -> ConfigFile:
        if not self.config_file_path:
            return ConfigFile()
        with open(self.config_file_path) as file:
            data = json.load(file)
            config = ConfigFile.parse_obj(data)
        return config


@dataclass
class ConfigService(Service):
    config_file_service: ConfigFileService
    profile_name: Optional[str] = None
    overrides: Optional[dict] = None

    def _merge_overrides(self, config: Settings) -> Settings:
        if self.overrides is None:
            return config
        return Settings(**{**config.dict(), **self.overrides})

    def _get_profile_config(self, config_file) -> Settings:
        profile_name = self.profile_name or config_file.default_profile
        if profile_name is None:
            return Settings()
        for profile in config_file.profiles:
            if profile.name == profile_name:
                return profile.config
        raise ValueError(f'Profile "{profile_name}" not found')

    @as_result(ValueError)
    def execute(self) -> Settings:
        config_file = self.config_file_service.execute().unwrap_or_throw()
        profile_config = self._get_profile_config(config_file=config_file)
        return self._merge_overrides(profile_config)
