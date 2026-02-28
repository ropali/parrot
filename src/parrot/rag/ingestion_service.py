from datetime import datetime
from enum import StrEnum
from pydantic import BaseModel


class JobStatus(StrEnum):
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class IngestionJob(BaseModel):
    id: str
    source_path: str
    status: JobStatus
    error: str | None
    created_at: datetime
    updated_at: datetime
