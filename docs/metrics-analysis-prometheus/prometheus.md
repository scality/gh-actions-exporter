# Prometheus

## Introduction

Prometheus is integrated with our `gh_actions_exporter` repository,
enabling the export of GitHub Actions metrics.

Prometheus is a powerful open-source monitoring and alerting system that allows
users to collect, store, and analyze time-series data. In this guide, we will
explore how to effectively utilize Prometheus to analyze GitHub Actions.

## Understanding Prometheus Queries

The idea here is not to recreate the entire Prometheus documentation; we will
simply discuss the key points to get you started easily without getting lost in
the plethora of information available on the Internet. I will redirect you to
the [documentation](https://prometheus.io/docs/introduction/overview/)
if you want to develop deeper.

To proceed, I will take a typical query and break it down, discussing other
potentially useful information to cover.

Let's examining this example query:

```bash
topk(5, sum(increase(github_actions_job_cost_count_total{repository=~"$repository", runner_type=~"$runner_type", repository_visibility=~"$repository_visibility", cloud=~"$cloud"}[$__range])) by (repository) > 0)
```

This query retrieves data related to GitHub Actions job costs and
provides the top 5 repositories with the highest cumulative cost
within a specified time range.

1. The query starts with the topk(5, ...) function, which returns the
   top 5 values based on a specified metric or condition.
2. The sum(increase(...)) part of the query calculates the cumulative
   sum of the specified metric. In our example, it calculates the
   cumulative sum of the github_actions_job_cost_count_total metric,
   representing the total job cost count.
3. Within the curly braces {}, we apply filters to narrow down the
   data based on specific criteria. The `$variable` refers to the filter
   variables that you can specify at the top of the page.
4. The `[$__range]` part specifies the time range for the query.
   It uses the `$__range` variable, which represents the selected time
   range in Grafana.
5. The `by (repository)` clause groups the data by the repository field.
   This enables the query to calculate the cost sum for each repository individually.
6. The expression `> 0` filters the query results to only include
   repositories with a value greater than zero.

It's also possible to combine different queries in Grafana. For example, one
query dividing by another.

Lastly, it is also important to understand `__interval`. `__interval`
represents the time interval between data points, whereas `__range`
represents the selected time range for the query.
