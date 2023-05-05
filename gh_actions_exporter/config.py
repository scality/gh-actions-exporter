import yaml
import os

from dotenv import load_dotenv
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
    load_dotenv()

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

    #display_statistics: bool = True
    # -> Pas fou finalement (sinon mettre ça partout dans les tests de `test_workflow`)

    #github_app_private_pem: SecretStr = os.getenv('GITHUB_APP_PRIVATE_PEM', '')
    github_app_id: int = int(os.getenv('GITHUB_APP_ID', '0'))
    github_app_installation_id: int = int(os.getenv('GITHUB_APP_INSTALLATION_ID', '0'))
    github_app_private_pem: SecretStr = """-----BEGIN RSA PRIVATE KEY-----
MIIEowIBAAKCAQEArv6ehMg8RhwbkfI6+nu+TLdhfpU0y+fYItwpV8/G0SjLMqWR
0t1h6Ow7VCM+XHTnAyo0pKe40tQoDkHiVqh0lK+otiWGzgtRG5iNztDR7ByLiInc
nNQnvWlqn9OqWeQBJOODGED7NwKwEv0yjtlyMIWwxGRARdE45jmkFh/Z/Q59Kj0Y
s3/xcmc1QyoDMbeuj2PGf2+HW7/bILYdu2vym96Iu24DyYdg3p3ty4sMRTzW+pTa
22tYH2uC+x8rOAHDJqXjzuJPCmkI3XzhTlBA0WlOYDNdhxwIhwPxsf+Hg/4Cx6Y4
J64Ok23jbnqVaIm7GEdl8fzgorWo+Ati8J+W0QIDAQABAoIBAH44q9AsucT8Kyq3
JLFdpiKhtxHdv2pAPVbPpIZxGP/uw7oxUKBfDGs8UYLbtPRtYd+XhscpLxfq7UVz
YjWNZiGFHlTbdoOSCBu2irqdRn1fDYobnmQEZvGpYr4Lp3kVC3o3HGzXGhxQtP3N
YbVFxKaZF6pggTeatMbi1qcarFpo8ar0rUpjJsL1ZGbkwCmr6D+Za5vk1qw1tu5I
MP/bVxhTc2ICz3jb9GHHxO5pb4ynCh1esid/6scFURpL0qevHtTaeTCHlwW+WaX3
KJzgxHOwopVgdKCN8o6ZdLZAfkzDHVFmJVPJ8yjxXHGMFPlhMHlKSnclB8fXNfMA
wsppdsECgYEA5YDFTKhgUgXIBOo8jF0zUNWrKFm9sGKwvSe01D2WGCwX59dCmqGd
Ig3+nkQVrLYq3+Uhp2cbWDubDqsgs7TLv3p/d7DM5ak991zX4uWwQ6oJhFQgCbix
GWKbgpYJCE+v7PwGtB+55ujM/2fn3sEezkEZoAjzSUSIFYd4h2pJkbkCgYEAwzLJ
/O34E834tNwWNfGakKU8Xe7X3sxTAY09XFDba7Ygc/Hi3c3O6V/tutfk5uj4mCxp
wN1vGYnW2tpsD+/Q+RiRgoQvT7abnOXc38Gcm5bwq7xwa9RtB4UsaraetnVHaEQ7
JRMY9aNQiwVlI3d+iouNLOE8gOpjM8GN75VIGdkCgYBrpd7legTT9EpBo+0KmZy8
SbyijJVg6qmjz8AN3WVNqUD9Sga/qRafJplLevv/quKpajxC3SYCWNL+Kl6IbEE1
ayvm5FL3Vk7ue+n3T21CD7uvChaM+Mh487uloOJTt6z5J62tR0RXftLI6d/kqAjf
DcILQqd6sl5yWry6J6yiYQKBgQCPBBpMD8rwL7wmPw6i7WbSzc3iAMn3Onsiquon
RjLNwz4Z1ULkQhN0l81lVSMoL89cJ0ZAgb0R2BUselYsgwf4ShDqsJC9dcyj8yKW
apOkx72EBmfUCWrs1J0LfsvgYSM1eLBg5JIn/0VW5lgI2VdEiSShmlErHxAZ7plg
zV5rWQKBgCD1r9ri5fpDDVayg1G7WaY3dtVyHBJ0d9/uAYdCn0rrCGlACkQpaepd
2vvSXP/2fIn35E2yo9pSoxtqX9cau9aQSBXhnYrjUBhqnfHFuDAx+Fxb0rwX7Biu
fjH2zsI+V58PDR4ML9DKeDt2Aj5FPw4nWZmuATrpheRu968UY/Ug
-----END RSA PRIVATE KEY-----"""

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
