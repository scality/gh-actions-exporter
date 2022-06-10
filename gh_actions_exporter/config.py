import yaml
from pathlib import Path
from typing import Dict, Any, List, Optional

from pydantic import BaseModel, BaseSettings


def yaml_config_settings_source(settings: BaseSettings) -> Dict[str, Any]:
    """
    A simple settings source that loads variables from a yaml file

    """
    config_file: Path = settings.__config__.config.config_file
    if config_file:
        return yaml.full_load(config_file.read_text())
    return {}


class Relabel(BaseModel):
    label: str
    description: Optional[str]
    default: Optional[str] = None
    values: List[str]


class ConfigFile(BaseSettings):
    config_file: Optional[Path]


class Settings(BaseSettings):
    job_relabelling: Optional[List[Relabel]] = []

    class Config:
        config: ConfigFile = ConfigFile()

        @classmethod
        def customise_sources(
            cls,
            init_settings,
            env_settings,
            file_secret_settings,
        ):
            return (
                init_settings,
                yaml_config_settings_source,
                env_settings,
                file_secret_settings,
            )
