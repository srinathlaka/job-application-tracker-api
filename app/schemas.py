from pydantic import BaseModel
from typing import Literal

ApplicationStatus = Literal[
    "Preparing",
    "Applied",
    "Interview Scheduled",
    "Rejected",
    "Accepted"
]


class JobApplicationCreate(BaseModel):
    company: str
    position: str
    status: ApplicationStatus
    german_required: bool
    location: str | None = None
    notes: str | None = None


class JobApplicationUpdate(BaseModel):
    company: str | None = None
    position: str | None = None
    status: ApplicationStatus | None = None
    german_required: bool | None = None
    location: str | None = None
    notes: str | None = None