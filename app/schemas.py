from pydantic import BaseModel
from pydantic import Field
from typing import Literal
from datetime import datetime

ApplicationStatus = Literal[
    "Preparing",
    "Applied",
    "Interview Scheduled",
    "Rejected",
    "Accepted"
]

DocumentType = Literal[
    "CV",
    "Cover Letter",
    "Additional"
]


class ApplicationDocumentResponse(BaseModel):
    id: int
    application_id: int
    document_type: DocumentType
    file_name: str
    file_path: str
    uploaded_at: datetime

    class Config:
        from_attributes = True


class JobApplicationCreate(BaseModel):
    company: str
    position: str
    status: ApplicationStatus
    german_required: bool
    location: str | None = None
    notes: str | None = None
    job_link: str | None = None


class JobApplicationUpdate(BaseModel):
    company: str | None = None
    position: str | None = None
    status: ApplicationStatus | None = None
    german_required: bool | None = None
    location: str | None = None
    notes: str | None = None
    job_link: str | None = None


class JobApplicationResponse(JobApplicationCreate):
    id: int
    created_at: datetime
    documents: list[ApplicationDocumentResponse] = Field(default_factory=list)

    class Config:
        from_attributes = True