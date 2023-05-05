
from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class Steps(BaseModel):
    name: str
    status: str
    conclusion: Optional[str] = None
    number: int
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


class WorkflowJob(BaseModel):
    id: int
    run_id: int
    run_url: str
    run_attempt: int
    runner_name: Optional[str] = None
    node_id: str
    head_sha: str
    url: str
    html_url: str
    status: str
    conclusion: Optional[str] = None
    started_at: datetime
    completed_at: Optional[datetime] = None
    name: str
    labels: list[str]
    steps: Optional[list[Steps]] = None


class WorkflowRun(BaseModel):
    id: int
    name: str
    event: str
    status: str
    conclusion: Optional[str] = None
    head_sha: str
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
    settings: dict
    workflow_run: dict
    jobs_cost: list[dict]
    total_cost: float
