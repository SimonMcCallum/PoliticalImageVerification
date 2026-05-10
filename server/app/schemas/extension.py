"""Pydantic schemas for the extension-sourced endpoints."""

import uuid
from datetime import datetime

from pydantic import BaseModel, Field

from app.models.extension import FlagReason, FlagStatus, ReportStatus
from app.schemas.verification import PDQ_PATTERN, PHASH_PATTERN, SHA256_PATTERN


class ExtensionReportRequest(BaseModel):
    """Extension-observed image with a promoter statement that did not match the register."""

    sha256: str | None = Field(default=None, pattern=SHA256_PATTERN)
    pdq: str | None = Field(default=None, pattern=PDQ_PATTERN)
    phash: str | None = Field(default=None, pattern=PHASH_PATTERN)
    detected_promoter_text: str | None = Field(default=None, max_length=2000)
    page_url_host: str | None = Field(default=None, max_length=255)


class ExtensionReportResponse(BaseModel):
    accepted: bool
    report_id: uuid.UUID | None = None
    observed_count: int | None = None
    # If True the report was absorbed into an existing entry because
    # we have already seen an image with the same perceptual hash.
    deduplicated: bool = False


class ExtensionFlagRequest(BaseModel):
    sha256: str | None = Field(default=None, pattern=SHA256_PATTERN)
    pdq: str | None = Field(default=None, pattern=PDQ_PATTERN)
    phash: str | None = Field(default=None, pattern=PHASH_PATTERN)
    reason: FlagReason
    note: str | None = Field(default=None, max_length=280)
    page_url_host: str | None = Field(default=None, max_length=255)


class ExtensionFlagResponse(BaseModel):
    accepted: bool
    flag_id: uuid.UUID | None = None


class ReviewQueueEntry(BaseModel):
    id: uuid.UUID
    sha256: str | None = None
    pdq: str | None = None
    phash: str | None = None
    detected_promoter_text: str | None = None
    page_url_host: str | None = None
    observed_count: int
    first_seen: datetime
    last_seen: datetime
    status: ReportStatus
    resolved_asset_id: uuid.UUID | None = None


class FlagQueueEntry(BaseModel):
    id: uuid.UUID
    sha256: str | None = None
    pdq: str | None = None
    phash: str | None = None
    reason: FlagReason
    note: str | None = None
    page_url_host: str | None = None
    status: FlagStatus
    created_at: datetime
