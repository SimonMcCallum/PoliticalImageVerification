import uuid
from datetime import datetime, timezone
from enum import Enum as PyEnum

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, Text, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class AssetStatus(str, PyEnum):
    ACTIVE = "active"
    REVOKED = "revoked"
    EXPIRED = "expired"


class Asset(Base):
    __tablename__ = "assets"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    party_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("parties.id"), nullable=False
    )
    submitted_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("party_users.id"), nullable=False
    )

    original_filename_encrypted: Mapped[str] = mapped_column(Text, nullable=False)
    mime_type: Mapped[str] = mapped_column(String(100), nullable=False)
    file_size: Mapped[int] = mapped_column(Integer, nullable=False)

    # Cryptographic hash for exact matching
    sha256_hash: Mapped[str] = mapped_column(String(64), nullable=False, index=True)

    # Perceptual hashes for fuzzy matching (stored as hex strings)
    pdq_hash: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    pdq_quality: Mapped[int] = mapped_column(Integer, nullable=False)
    phash: Mapped[str] = mapped_column(String(16), nullable=False, index=True)

    # Encrypted storage reference
    encrypted_storage_key: Mapped[str] = mapped_column(String(500), nullable=False)
    encryption_iv: Mapped[str] = mapped_column(String(32), nullable=False)

    # Badge and verification
    badge_storage_key: Mapped[str | None] = mapped_column(String(500), nullable=True)
    qr_code_storage_key: Mapped[str | None] = mapped_column(String(500), nullable=True)
    verification_id: Mapped[str] = mapped_column(
        String(12), nullable=False, unique=True, index=True
    )

    # Metadata
    metadata_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    status: Mapped[AssetStatus] = mapped_column(
        Enum(AssetStatus), default=AssetStatus.ACTIVE, nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    expires_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    revoked_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    party: Mapped["Party"] = relationship(back_populates="assets")
    submitter: Mapped["PartyUser"] = relationship()
    verification_logs: Mapped[list["VerificationLog"]] = relationship(
        back_populates="asset"
    )
