"""Email processing job model for tracking email-submitted image processing."""

import uuid
from datetime import datetime, timezone
from enum import Enum as PyEnum

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class EmailJobStatus(str, PyEnum):
    PENDING_VERIFICATION = "pending_verification"
    VERIFIED = "verified"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class EmailProcessingJob(Base):
    __tablename__ = "email_processing_jobs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    party_user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("party_users.id"), nullable=False
    )
    sender_email_hash: Mapped[str] = mapped_column(
        String(64), nullable=False
    )
    status: Mapped[EmailJobStatus] = mapped_column(
        Enum(EmailJobStatus), default=EmailJobStatus.PENDING_VERIFICATION, nullable=False
    )
    image_storage_key: Mapped[str | None] = mapped_column(String(500), nullable=True)
    result_storage_key: Mapped[str | None] = mapped_column(String(500), nullable=True)
    add_promoter: Mapped[bool] = mapped_column(Boolean, default=True)
    position: Mapped[str] = mapped_column(String(20), default="bottom-left")
    verification_token_hash: Mapped[str | None] = mapped_column(String(64), nullable=True)
    verification_expires: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    party_user: Mapped["PartyUser"] = relationship()  # noqa: F821
