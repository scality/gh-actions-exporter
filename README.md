# [Abandoned]

This repository holds some helm chart fixes that were missing in original project that rendered the project undeployable for me. Eventually we started sourcing metrics from Github Runner Scale Set controller and this project became unnecessary.

# GitHub WebHook Exporter

The idea of this exporter is to be able to expose this service to listen
from WebHooks coming from GitHub.
Then expose those metrics in OpenMetrics format for later usage.

## Install

To install and use this project, please make sure you have [poetry](https://python-poetry.org/) installed.

Then run:
```shell
poetry install
```

## Start

To start the API locally you can use the following command:

```shell
poetry run start
```
