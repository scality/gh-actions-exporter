import time
from githubkit import GitHub, AppInstallationAuthStrategy

from gh_actions_exporter.config import Settings

class TokenGenerator:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.github_app_private_key: str = settings.github_app_private_key.get_secret_value()
        self.github_app_id: int = int(settings.github_app_id)
        self.github_app_installation_id :int = int(settings.github_app_installation_id)

    def generate_token(self) -> GitHub:
        github = GitHub(
            AppInstallationAuthStrategy(
                self.github_app_id, self.github_app_private_key, self.github_app_installation_id
            )
        )
        return github
