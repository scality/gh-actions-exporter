# GitHub Actions Exporter

The GitHub Actions Exporter is a project used to retrieve information
provided by GitHub, notably through Webhooks, process it, and store it
via Prometheus. Later on, Grafana is employed to display and visualize
the data in graphs.

The main idea of this exporter is to be able to expose this service to
listen from WebHooks coming from GitHub.
