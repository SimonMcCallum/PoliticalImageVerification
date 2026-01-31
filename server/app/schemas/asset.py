import uuid
from datetime import datetime

from pydantic import BaseModel

from app.models.asset import AssetStatus


class AssetResponse(BaseModel):
    id: uuid.UUID
    party_id: uuid.UUID
    mime_type: str
    file_size: int
    sha256_hash: str
    pdq_hash: str
    pdq_quality: int
    phash: str
    verification_id: str
    verification_url: str
    badge_url: str | None
    qr_code_url: str | None
    metadata: dict | None
    status: AssetStatus
    created_at: datetime
    expires_at: datetime | None

    model_config = {"from_attributes": True}


class AssetListItem(BaseModel):
    id: uuid.UUID
    verification_id: str
    mime_type: str
    file_size: int
    status: AssetStatus
    created_at: datetime

    model_config = {"from_attributes": True}


class AssetMetadataUpdate(BaseModel):
    metadata: dict | None = None
    status: AssetStatus | None = None
