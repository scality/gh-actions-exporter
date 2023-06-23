# Prometheus

## Introduction

Prometheus is a powerful open-source monitoring and alerting system that allows
users to collect, store, and analyze time-series data. In this guide, we will
explore how to effectively utilize Prometheus to analyze GitHub Actions.

To collect and analyze GitHub Actions metrics, users need to have an existing
Prometheus installation and configure it to pull metrics. This requires
specifying the Prometheus URL with the `/metrics` path.

## Understanding Prometheus Queries

The idea here is not to recreate the entire Prometheus documentation; we will
simply discuss the key points to get you started easily without getting lost in
the plethora of information available on the Internet.

To learn more about Prometheus itself, checkout the official
[documentation](https://prometheus.io/docs/introduction/overview/),
as well as [querying Prometheus](https://prometheus.io/docs/prometheus/latest/querying/basics/).

To proceed, I will take a typical query and break it down, discussing other
potentially useful information to cover.

Let's examining this example query:

```bash
topk(5, sum(increase(github_actions_job_cost_count_total{}[5m]])) by (repository) > 0)
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
3. The `[5m]` part specifies the time range for the query.
4. The `by (repository)` clause groups the data by the repository label.
   This enables the query to calculate the cost sum for each repository individually.
5. The expression `> 0` filters the query results to only include
   repositories with a value greater than zero.

!!! info

    Using Grafana enhances the visualization of Prometheus data and
    provides powerful querying capabilities. Within Grafana, apply filters,
    combine queries, and utilize variables for dynamic filtering. It's important
    to understand `__interval` (time interval between data points) and `__range`
    (selected time range) when working with Prometheus data in Grafana. This
    integration enables efficient data exploration and analysis for better
    insights and decision-making.
