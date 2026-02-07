import uuid
from datetime import datetime

from pydantic import BaseModel

from app.models.email_job import EmailJobStatus


class EmailJobResponse(BaseModel):
    id: uuid.UUID
    status: EmailJobStatus
    created_at: datetime
    completed_at: datetime | None

    model_config = {"from_attributes": True}


class EmailVerificationConfirm(BaseModel):
    token: str
