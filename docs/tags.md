# Tags

In addition to Grafana, we also have tags that are set on AWS and GCP to
visualize data. These tags allow us to navigate their respective consoles
and filter data using specific tags, providing more accurate figures
compared to Grafana, which has an approximate margin of error of +/- 5%.

## AWS

For AWS, we have the following tags (specified in the configuration file
found in the `devinfra` repository):

- Name of the runner
- `lifecycle_autostop`: `no`
- `lifecycle_autostart`: `no`
- `map-migrated`: `mig42992`
- `owner`: `ci`
- `tool`: `runner-manager`

## GCloud

For GCP, we have the following tags (retrieve dynamic tags using the
`gh_actions_exporter` repository via webhooks):

- machine_type
- image
- status
- repository
- workflow
- job
