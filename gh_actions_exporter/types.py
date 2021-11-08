
from datetime import datetime
from typing import Optional
from pydantic import BaseModel


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
    updated_at: datetime or None


class Repository(BaseModel):
    name: str
    full_name: str


class WebHook(BaseModel):
    workflow_run: Optional[WorkflowRun] = None
    repository: Repository
