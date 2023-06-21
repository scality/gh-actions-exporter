# Collected and reported metrics

In first place, it is important to differentiate the `workflow_run`
and the `workflow_job` webhook events.

The `workflow_run` request is triggered when a workflow run is `requested`,
`in_progress`, `completed` or `failure`. However, for this project, we are not
interested in the `cancelled` or `skipped` events, so we will ignore them.

On the other hand, the `workflow_job` request is triggered when a
workflow job is `queued`, `in_progress`, or `completed`. We will also ignore
the `cancelled` or `skipped` events for `workflow_job` in this project.

## Workflow run

Here are the different metrics collected by the GitHub Actions Exporter
project for workflow runs:

The number of workflow rebuilds: `github_actions_workflow_rebuild_count`.

The duration of a workflow in seconds: `github_actions_workflow_duration_seconds`.

Count the number of workflows for each state:

- `github_actions_workflow_failure_count`
- `github_actions_workflow_success_count`
- `github_actions_workflow_cancelled_count`
- `github_actions_workflow_inprogress_count`
- `github_actions_workflow_total_count`

## Workflow job

Here are the different metrics collected by the GitHub Actions
Exporter project for workflows and jobs.

The duration of a job in seconds: `github_actions_job_duration_seconds`.

Time between when a job is requested and started: `github_actions_job_start_duration_seconds`.

Count the number of jobs for each states:

- `github_actions_job_failure_count`
- `github_actions_job_success_count`
- `github_actions_job_cancelled_count`
- `github_actions_job_inprogress_count`
- `github_actions_job_queued_count`
- `github_actions_job_total_count`

## Cost metric

This is the last metric we collect, and it is one of the most important
ones. It allows us to determine the cost of our CI runs.

### Formula

Here is the formula to calculate the cost over a period of time:

```bash
cost = duration (per second) / 60 * cost (per minute)
```

### How do we find the cost per minute?

#### GitHub

As for GitHub, it is quite simple. They provide us with a fixed value, and
the price never varies. To give an example, for `ubuntu-latest`, we have a cost
of 0.008$/min, that's it. Easy!

For larger GitHub hosted runners, such as the high-performance options, the
pricing structure may differ. The exact details and costs associated with those
specific runner types can be obtained from
[GitHub's documentation](https://docs.github.com/en/billing/managing-billing-for-github-actions/about-billing-for-github-actions).

#### Self-Hosted

When it comes to the cost of self-hosted runners, it's a bit more complicated.

To calculate the costs of self-hosted runners, we can play the game of
calculating for the main ones, namely AWS and Google Cloud Provider (GCP).

The cost can be found based on the machine type in the Management Console
for AWS (when creating an EC2 instance) and on the
[Google Cloud website](https://cloud.google.com/compute/vm-instance-pricing)
for GCP.

We aim to obtain a result that is close to reality, within a range of
approximately +/- 5%, for data visualization purposes.
Key points to consider for retrieving cost information:

- RAM and CPU Costs : provided cost per minute for RAM and CPU expenses, can
  be found in the documentation of the respective cloud provider.
- Storage Costs : provided cost per minute for storage expenses, can
  be found in the documentation of the respective cloud provider.
- Bandwidth Cost: Directly determining the cost per minute of bandwidth is
  not feasible.

Calculating the bandwidth cost per minutes is up to the discretion of the
user and will vary depending on the workload. As an example, adding an
extra 30% is what we found by comparing the values in the documentation
of different cloud providers (for CPU, RAM, and storage) with the actual
values available on our invoices. Using this information, we were able
to estimate the overall cost using the following formula:
(all costs are per minute)

```bash
cost = (cost_per_flavor + cost_per_storage) * cost_of_bandwidth / 100
```

<!-- trunk:ignore

!!! note

    GCP and AWS costs are quite the same for the same flavors.

-->

### The different tags and their associated cost

| Provider | Runner               | Cost ($ per min) |
| -------- | -------------------- | ---------------- |
| GitHub   | `ubuntu-latest`      | 0.008            |
| GitHub   | `ubuntu-18.04`       | 0.008            |
| GitHub   | `ubuntu-20.04`       | 0.008            |
| GitHub   | `ubuntu-22.04`       | 0.008            |
| GitHub   | `ubuntu-20.04-4core` | 0.016            |
| GitHub   | `ubuntu-22.04-4core` | 0.016            |
| GitHub   | `ubuntu-22.04-8core` | 0.032            |
| AWS      | `t3.small`           | 0.000625         |
| GCP      | `n2-standard-2`      | 0.0025           |
| AWS      | `t3.large`           | 0.0025           |
| GCP      | `n2-standard-4`      | 0.005            |
| GCP      | `n2-standard-8`      | 0.01             |

<!-- trunk:ignore

!!! note

    Please note that the names of large GitHub hosted runners
    may not be explicitly the same as shown below, but this is
    the naming convention recommended by GitHub.

-->
