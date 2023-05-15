from gh_actions_exporter.cost import Cost


def test_get_job_cost(workflow_job, settings):
    assert Cost(settings).get_job_cost(workflow_job, "large") == 0.16


def test_job_cost_unknown_label(workflow_job, settings):
    assert Cost(settings).get_job_cost(workflow_job, "xxx") == 0
