import time
from github import Github, GithubIntegration, AppAuthentication

from gh_actions_exporter.config import Settings

class TokenGenerator:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.github_app_private_key: str = settings.github_app_private_key.get_secret_value()
        self.github_app_id: int = int(settings.github_app_id)
        self.github_app_installation_id :int = int(settings.github_app_installation_id)

    def generate_token(self) -> Github:
        g: Github = Github(
            app_auth=AppAuthentication(
                app_id=self.github_app_id,
                private_key=self.github_app_private_key,
                installation_id=self.github_app_installation_id,
            ),
        )
        return g
