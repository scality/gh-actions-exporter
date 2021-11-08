
from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class CheckSuite(BaseModel):
    id: int
    name: str
    status: str
    conclusion: str or None
    head_sha: str
    head_branch: str
    started_at: datetime
    completed_at: datetime or None


class Repository(BaseModel):
    name: str
    full_name: str


class WebHook(BaseModel):
    check_suite: Optional[CheckSuite] = None
    repository: Repository
