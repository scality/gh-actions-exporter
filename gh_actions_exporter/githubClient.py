from githubkit import AppInstallationAuthStrategy, GitHub

from gh_actions_exporter.config import Settings


class GithubClient:
    def __init__(self, settings: Settings) -> None:
        self.auth = GitHub(
            AppInstallationAuthStrategy(
                int(settings.github_app_id),
                settings.github_app_private_key.get_secret_value(),
                int(settings.github_app_installation_id)
            )
        )
