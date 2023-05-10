from datetime import datetime
from typing import Optional
from gh_actions_exporter.config import Settings
from githubkit.rest import Job

from pydantic import BaseModel, Field
from githubkit.utils import UNSET, Missing
from typing import Any, List, Union, Literal



class Steps(BaseModel):
    name: str
    status: str
    conclusion: Optional[str] = None
    number: int
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


class JobPropStepsItems(BaseModel):
    status: str
    conclusion: str
    name: str
    number: int
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


class WorkflowJob(BaseModel):
    id: int = Field(default=...)
    run_id: float = Field(default=...)
    run_attempt: int = Field(default=...)
    run_url: str = Field(default=...)
    head_sha: str = Field(default=...)
    node_id: str = Field(default=...)
    name: str = Field(default=...)
    check_run_url: str = Field(default=...)
    html_url: str = Field(default=...)
    url: str = Field(default=...)
    status: Literal["queued", "in_progress", "completed"] = Field(
        description="The current status of the job. Can be `queued`, `in_progress`, or `completed`.",
        default=...,
    )
    steps: List[JobPropStepsItems] = Field(
        default=...
    )
    conclusion: Union[
        None, Literal["success", "failure", "cancelled", "skipped"]
    ] = Field(default=...)
    labels: List[str] = Field(
        description='Custom labels for the job. Specified by the [`"runs-on"` attribute](https://docs.github.com/en/actions/reference/workflow-syntax-for-github-actions#jobsjob_idruns-on) in the workflow YAML.',
        default=...,
    )
    runner_id: Union[int, None] = Field(
        description="The ID of the runner that is running this job. This will be `null` as long as `workflow_job[status]` is `queued`.",
        default=...,
    )
    runner_name: Union[str, None] = Field(
        description="The name of the runner that is running this job. This will be `null` as long as `workflow_job[status]` is `queued`.",
        default=...,
    )
    runner_group_id: Union[int, None] = Field(
        description="The ID of the runner group that is running this job. This will be `null` as long as `workflow_job[status]` is `queued`.",
        default=...,
    )
    runner_group_name: Union[str, None] = Field(
        description="The name of the runner group that is running this job. This will be `null` as long as `workflow_job[status]` is `queued`.",
        default=...,
    )
    workflow_name: Union[str, None] = Field(
        description="The name of the workflow.", default=...
    )
    head_branch: Union[str, None] = Field(
        description="The name of the current branch.", default=...
    )
    started_at: datetime = Field(default=...)
    completed_at: Union[datetime, None] = Field(default=...)
    created_at: datetime = Field(default=...)


class WorkflowRun(BaseModel):
    id: int
    name: str
    event: str
    status: str
    head_sha: Optional[str] = None
    conclusion: Optional[str] = None
    workflow_id: int
    run_number: int
    head_branch: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    run_attempt: int
    run_started_at: Optional[datetime] = None


class Repository(BaseModel):
    name: str
    full_name: str
    visibility: str


class Organization(BaseModel):
    login: str


class WebHook(BaseModel):
    workflow_run: Optional[WorkflowRun] = None
    workflow_job: Optional[WorkflowJob] = None
    repository: Optional[Repository] = None
    organization: Optional[Organization] = None
    zen: Optional[str] = None


class JobCost(BaseModel):
    name: str
    cost: int


class CheckRunData(BaseModel):
    summary: str
    settings: Settings
    workflow_run: WorkflowRun
    jobs_cost: list[JobCost]
    total_cost: float

class DataModelOutput(BaseModel):
    title: str
    summary: str

class DataModel(BaseModel):
    name: str
    head_sha: str
    status: str
    conclusion: str
    output: DataModelOutput
