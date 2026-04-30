"""Models for extension-sourced data: potential breach reports and user flags.

A ``ExtensionReport`` is an extension-observed image that carries a
promoter statement but is not currently in the register. Reports are
de-duplicated by perceptual hash. They feed the administrative review
queue.

A ``ExtensionFlag`` is a user-initiated flag raised through the extension
context menu. Flags carry a reason code and optional short note.
"""

import uuid
from datetime import datetime, timezone
from enum import Enum as PyEnum

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class ReportStatus(str, PyEnum):
    OPEN = "open"
    TRIAGED = "triaged"
    REGISTERED_AUTHORITY_SUPPLIED = "registered_authority_supplied"
    DISMISSED = "dismissed"


class FlagReason(str, PyEnum):
    MISATTRIBUTED = "misattributed"
    PROMOTER_STATEMENT_FAKE = "promoter_statement_fake"
    CONTENT_CONCERN = "content_concern"
    OTHER = "other"


class FlagStatus(str, PyEnum):
    OPEN = "open"
    TRIAGED = "triaged"
    REFERRED = "referred"
    DISMISSED = "dismissed"


class ExtensionReport(Base):
    """Extension-observed image carrying a promoter statement but not registered.

    Reports are de-duplicated on ``pdq_hash`` (falling back to ``sha256``
    when no PDQ was supplied) so repeated observations of the same image
    increment ``observed_count`` rather than creating new rows.
    """

    __tablename__ = "extension_reports"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )

    sha256_hash: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    pdq_hash: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    phash: Mapped[str | None] = mapped_column(String(16), nullable=True, index=True)

    # Detected promoter-statement text as extracted by the extension's OCR.
    # Stored plain because there is no PII here: the promoter statement
    # itself is published information.
    detected_promoter_text: Mapped[str | None] = mapped_column(Text, nullable=True)

    # The HOST of the page where the image was observed (e.g. "facebook.com").
    # The full URL is never stored.
    page_url_host: Mapped[str | None] = mapped_column(String(255), nullable=True)

    observed_count: Mapped[int] = mapped_column(Integer, nullable=False, default=1)

    first_seen: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    last_seen: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    status: Mapped[ReportStatus] = mapped_column(
        Enum(ReportStatus), nullable=False, default=ReportStatus.OPEN
    )

    # If the admin resolved this report by registering the image as
    # authority-supplied, the resulting asset is linked here.
    resolved_asset_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("assets.id"), nullable=True
    )
    resolved_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("party_users.id"), nullable=True
    )
    resolved_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )


class ExtensionFlag(Base):
    """User-initiated flag raised through the extension context menu."""

    __tablename__ = "extension_flags"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )

    sha256_hash: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    pdq_hash: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    phash: Mapped[str | None] = mapped_column(String(16), nullable=True, index=True)

    reason: Mapped[FlagReason] = mapped_column(Enum(FlagReason), nullable=False)
    note: Mapped[str | None] = mapped_column(String(280), nullable=True)

    page_url_host: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # SHA-256 of the submitter's IP. Stored only for rate limiting and
    # abuse detection. Cannot be reversed.
    source_ip_hash: Mapped[str | None] = mapped_column(String(64), nullable=True)

    status: Mapped[FlagStatus] = mapped_column(
        Enum(FlagStatus), nullable=False, default=FlagStatus.OPEN
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    triaged_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("party_users.id"), nullable=True
    )
    triaged_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
