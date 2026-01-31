import uuid
from datetime import datetime, timezone
from enum import Enum as PyEnum

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class MatchType(str, PyEnum):
    EXACT = "exact"
    PERCEPTUAL = "perceptual"
    NONE = "none"


class VerificationResult(str, PyEnum):
    VERIFIED = "verified"
    UNVERIFIED = "unverified"
    PARTIAL_MATCH = "partial_match"
    ERROR = "error"


class VerificationLog(Base):
    __tablename__ = "verification_logs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    asset_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("assets.id"), nullable=True
    )
    match_type: Mapped[MatchType] = mapped_column(Enum(MatchType), nullable=False)
    pdq_distance: Mapped[int | None] = mapped_column(Integer, nullable=True)
    phash_distance: Mapped[int | None] = mapped_column(Integer, nullable=True)
    source_ip_hash: Mapped[str | None] = mapped_column(String(64), nullable=True)
    result: Mapped[VerificationResult] = mapped_column(
        Enum(VerificationResult), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    asset: Mapped["Asset | None"] = relationship(back_populates="verification_logs")


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    actor_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), nullable=True
    )
    action: Mapped[str] = mapped_column(String(100), nullable=False)
    entity_type: Mapped[str] = mapped_column(String(50), nullable=False)
    entity_id: Mapped[str] = mapped_column(String(50), nullable=False)
    details_encrypted: Mapped[str | None] = mapped_column(String(2000), nullable=True)
    ip_hash: Mapped[str | None] = mapped_column(String(64), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
