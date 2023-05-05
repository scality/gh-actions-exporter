import time
from github import GithubIntegration

from gh_actions_exporter.config import Settings

class TokenGenerator:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.github_app_private_pem: str = settings.github_app_private_pem.get_secret_value()
        self.github_app_id: int = int(settings.github_app_id)
        self.github_app_installation_id :int = int(settings.github_app_installation_id)

    def generate_token(self) -> bytes:
        integration: GithubIntegration = GithubIntegration(integration_id=self.github_app_id, private_key=self.github_app_private_pem)
        access_token: str = integration.get_access_token(self.github_app_installation_id).token
        return access_token
