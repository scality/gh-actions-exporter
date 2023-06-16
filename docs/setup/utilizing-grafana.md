# Utilizing Grafana

It is possible to visualize the data provided by `gh_actions_exporter` with Grafana.

Grafana is a powerful open-source platform that allows users to visualize
and monitor various metrics and data sources. In this guide, we will
explore how to effectively use Grafana to monitor and analyze GitHub Actions.

## As a user

When accessing the Grafana URL, users can easily sort and filter the displayed
data using variables located at the top of the page. This functionality
allows more precise and targeted information based on specific criteria.

Available Sorting Options:

- `repository`: GitHub repository
- `workflow_name`: Name of the workflow
- `repository_visibility`: Public or private
- `job_name`: Name of the job
- `runner_type`: GitHub or self-hosted

Note that additional variables may be added in the future to enhance the
monitoring capabilities further.

It is possible to test and display specific information easily by
accessing the "Explore" tab in Grafana. You will need to enter a
query there, as explained in the "As a developer" section below.

## As a developper

Grafana provides a flexible platform for customization and extensibility.
Developpers can create their own dashboards, incorporating specific metrics and
visualizations tailored to their unique requirements.

I will not provide a comprehensive guide on Grafana; instead, I will
focus on key points to help you get started. I encourage you to refer
to [Grafana's documentation](https://grafana.com/docs/grafana/latest/dashboards/)
for more detailed information.

There are various types of graphs available in Grafana, including line charts,
bar charts, pie charts, and more. I encourage you to explore and experiment
with different graph types by referring to the documentation, exploring
existing graphs, or simply trying them out yourself.

### Query

First of all, to create a graph, start by clicking on the "Add panel" button
at the top of the page. Another option is to duplicate another graph if
you want to make a similar one.

Let's begin by examining an example query:

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

It's also possible to combine different queries in Grafana allowing you
to make other graphs. For example, one query dividing by another.

Lastly, it is also important to understand `__interval`. `__interval`
represents the time interval between data points, whereas `__range`
represents the selected time range for the query.
