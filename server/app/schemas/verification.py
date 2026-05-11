import uuid
from datetime import datetime

from pydantic import BaseModel, Field

from app.models.verification import MatchType, VerificationResult

# Reusable hex-only field patterns. Anchored to fixed lengths so we
# reject garbage at the schema layer rather than letting it flow into
# SQL WHERE clauses on indexed hash columns.
SHA256_PATTERN = r"^[0-9a-fA-F]{64}$"
PDQ_PATTERN = r"^[0-9a-fA-F]{64}$"   # PDQ is also 256 bits => 64 hex chars
PHASH_PATTERN = r"^[0-9a-fA-F]{16}$"  # pHash is 64 bits => 16 hex chars


class RiskAssessmentResponse(BaseModel):
    """Risk classification surfaced to the caller.

    See app/services/risk.py for the full decision table. The
    ``level`` and ``category`` fields are stable machine-readable
    codes; the ``explanation`` is intended for direct display to a
    voter or journalist.
    """

    level: str  # "ok" | "info" | "low" | "warn" | "high"
    category: str  # see RiskCategory enum in services/risk.py
    explanation: str
    suggested_action: str  # see SuggestedAction enum
    attributed_party_name: str | None = None
    attributed_party_id: str | None = None
    promoter_text_present: bool = False
    promoter_pattern_matched: bool = False


class VerificationResponse(BaseModel):
    verified: bool
    result: VerificationResult
    match_type: MatchType
    confidence: float
    party: dict | None = None
    asset_id: uuid.UUID | None = None
    verification_id: str | None = None
    registered_date: datetime | None = None
    pdq_distance: int | None = None
    phash_distance: int | None = None
    # OCR-detected promoter info (when image is unverified but has promoter text).
    # Kept for backwards compatibility with the existing client; new
    # consumers should read the structured `risk` field instead.
    promoter_detected: bool = False
    promoter_party_name: str | None = None
    # Full risk classification.
    risk: RiskAssessmentResponse | None = None


class VerificationByIdResponse(BaseModel):
    verified: bool
    party_name: str | None = None
    party_short_name: str | None = None
    registered_date: datetime | None = None
    status: str | None = None
    verification_id: str


class HashVerifyRequest(BaseModel):
    sha256: str | None = Field(default=None, pattern=SHA256_PATTERN)
    pdq: str | None = Field(default=None, pattern=PDQ_PATTERN)
    phash: str | None = Field(default=None, pattern=PHASH_PATTERN)
