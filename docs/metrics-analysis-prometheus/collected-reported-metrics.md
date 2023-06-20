# Collected and reported metrics

The idea behind this repository is to gather as much information as
possible from the requests sent by GitHub via the Webhook.

In first place, it is important to differentiate the `workflow_run`
and the `workflow_job` API requests.

The `workflow_run` request is triggered when a workflow run is `requested`,
`in_progress`, or `completed`.

On the other hand, the `workflow_job` request is triggered when a
workflow job is `queued`, `in_progress`, or `completed`.

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

### The formula to calculate the cost over a period of time

To calculate this metric, we use the following formula:

```bash
cost = duration (per second) / 60 * cost (per minute)
```

### How do we find the cost per minute?

#### GitHub

As for GitHub, it is quite simple. They provide us with a fixed value, and
the price never varies. To give an example, for `ubuntu-latest`, we have a cost
of 0.008$/min, that's it. Easy!

#### Self-Hosted

When it comes to the cost of self-hosted runners, it's a bit more complicated.

To calculate the costs of self-hosted runners, we can play the game of
calculating for the main ones, namely AWS and Google Cloud Provider (GCP).

The cost can be found based on the machine type in the Management Console
for AWS (when creating an EC2 instance) and on the
[Google Cloud website](https://cloud.google.com/compute/vm-instance-pricing)
for GCP.

Unfortunately, these values are not accurate as they lack several elements
such as bandwidth or storage. As for storage costs, they can be found in
the same places where the machine type cost is available. However, it is
not possible to determine the bandwidth cost directly.

To overcome this, we had to devise a workaround. We didn't necessarily
need an exact cost for CI but rather a value close to reality (+/- 5%)
for data visualization purposes.

We analyzed previous invoices and calculated the additional cost generated
by bandwidth, which amounted to approximately 30% for each month.
Consequently, we were able to approximate the cost using the following formula:

```bash
cost = (cost_per_flavor + cost_per_storage) * 130 / 100
```

_Good news, GCP and AWS costs are quite the same for the same flavors._

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
