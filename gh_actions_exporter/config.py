import yaml
from enum import Enum
from pathlib import Path
from typing import Dict, Any, List, Optional

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
    name = 'name'
    label = 'label'


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
        'medium': 0.008,
        'large': 0.016,
        'xlarge': 0.032,
        '2xlarge': 0.064,
        '3xlarge': 0.128
    }
    flavor_label: Optional[str] = 'flavor'
    default_cost: Optional[float] = 0.008
    github_app_private_pem: SecretStr # Checker
    github_app_id: int
    github_app_installation_id: int
    title: str = "Workflow Costs"
    summary: str = """Behind a CI run, there are servers running which cost money, so it
                    is important to be careful not to abuse this feature to avoid wasting money."""

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
