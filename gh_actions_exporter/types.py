
from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class WorkflowJob(BaseModel):
    id: int
    run_id: int
    run_url: str
    run_attempt: int
    node_id: str
    head_sha: str
    url: str
    html_url: str
    status: str
    conclusion: Optional[str] = None
    started_at: datetime
    completed_at: Optional[datetime] = None
    name: str


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


class Repository(BaseModel):
    name: str
    full_name: str


class WebHook(BaseModel):
    workflow_run: Optional[WorkflowRun] = None
    workflow_job: Optional[WorkflowJob] = None
    repository: Repository
