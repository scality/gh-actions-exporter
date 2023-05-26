from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml
from pydantic import BaseModel, BaseSettings, SecretStr


def yaml_config_settings_source(settings: BaseSettings) -> Dict[str, Any]:
    """
    A simple settings source that loads variables from a yaml file

    """
    config_file: Path = settings.__config__.config.config_file
    if config_file:
        return yaml.full_load(config_file.read_text())
    return {}


class RelabelType(str, Enum):
    name = "name"
    label = "label"


class Relabel(BaseModel):
    label: str
    type: RelabelType = RelabelType.label
    description: Optional[str]
    default: Optional[str] = None
    values: List[str]


class ConfigFile(BaseSettings):
    config_file: Optional[Path]


class Settings(BaseSettings):
    job_relabelling: Optional[List[Relabel]] = []
    job_costs: Optional[Dict[str, float]] = {
        "ubuntu-latest": 0.008,
        "ubuntu-22.04": 0.008,
        "ubuntu-20.04": 0.008,
        "medium": 0.008,
        "large": 0.016,
        "xlarge": 0.032,
        "2xlarge": 0.064,
        "3xlarge": 0.128,
    }
    default_cost: Optional[float] = 0

    check_runs_enabled: bool = False
    github_app_id: Optional[int]
    github_app_installation_id: Optional[int]
    github_app_private_key: Optional[SecretStr]

    class Config:
        config: ConfigFile = ConfigFile()
        env_file = ".env"
        env_file_encoding = "utf-8"

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
