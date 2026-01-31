import uuid
from datetime import datetime

from pydantic import BaseModel

from app.models.verification import MatchType, VerificationResult


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


class VerificationByIdResponse(BaseModel):
    verified: bool
    party_name: str | None = None
    party_short_name: str | None = None
    registered_date: datetime | None = None
    status: str | None = None
    verification_id: str


class HashVerifyRequest(BaseModel):
    sha256: str | None = None
    pdq: str | None = None
    phash: str | None = None
