import uuid
from datetime import datetime

from pydantic import BaseModel, EmailStr

from app.models.party import PartyStatus, UserRole


class PartyCreate(BaseModel):
    name: str
    short_name: str
    registration_number: str | None = None
    contact_email: str | None = None


class PartyUpdate(BaseModel):
    name: str | None = None
    short_name: str | None = None
    registration_number: str | None = None
    contact_email: str | None = None
    status: PartyStatus | None = None


class PartyResponse(BaseModel):
    id: uuid.UUID
    name: str
    short_name: str
    registration_number: str | None
    status: PartyStatus
    created_at: datetime

    model_config = {"from_attributes": True}


class PartyPublicResponse(BaseModel):
    id: uuid.UUID
    name: str
    short_name: str
    status: PartyStatus

    model_config = {"from_attributes": True}


class PartyUserCreate(BaseModel):
    username: str
    email: str
    password: str
    role: UserRole = UserRole.SUBMITTER


class PartyUserResponse(BaseModel):
    id: uuid.UUID
    party_id: uuid.UUID
    username: str
    role: UserRole
    mfa_enabled: bool
    is_active: bool
    default_statement_position: str
    email_verified_for_processing: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class PromoterStatementUpdate(BaseModel):
    statement: str

    model_config = {"json_schema_extra": {"examples": [{"statement": "Authorised by J. Smith, 123 Main St, Wellington, for the Example Party"}]}}


class PromoterStatementResponse(BaseModel):
    statement: str | None
    updated_at: datetime | None
