# Runner Types

Metrics are labelled with the runner type. The logic for determining the runner type is as follows -

If the runner tag is in the [github_hosted_runner_labels](./gh_actions_exporter/config.py) list the runner type will be `github-hosted` else the runner type will be `self-hosted`. Additional `github-hosted` runner tags can be added via config.
