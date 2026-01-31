"""Party management endpoints."""

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import hash_password, require_admin
from app.core.database import get_db
from app.models.party import Party, PartyUser
from app.schemas.party import (
    PartyCreate,
    PartyPublicResponse,
    PartyResponse,
    PartyUpdate,
    PartyUserCreate,
    PartyUserResponse,
)
from app.services.encryption import encrypt_string

router = APIRouter(prefix="/parties", tags=["parties"])


@router.get("", response_model=list[PartyPublicResponse])
async def list_parties(db: AsyncSession = Depends(get_db)):
    """List all registered parties (public info only)."""
    result = await db.execute(select(Party).order_by(Party.name))
    parties = result.scalars().all()
    return parties


@router.post("", response_model=PartyResponse, status_code=status.HTTP_201_CREATED)
async def create_party(
    body: PartyCreate,
    user: PartyUser = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """Register a new political party (admin only)."""
    # Check for duplicate name
    existing = await db.execute(select(Party).where(Party.name == body.name))
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Party with this name already exists",
        )

    party = Party(
        name=body.name,
        short_name=body.short_name,
        registration_number=body.registration_number,
        contact_email_encrypted=(
            encrypt_string(body.contact_email) if body.contact_email else None
        ),
    )
    db.add(party)
    await db.commit()
    await db.refresh(party)
    return party


@router.get("/{party_id}", response_model=PartyResponse)
async def get_party(
    party_id: uuid.UUID,
    user: PartyUser = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Party).where(Party.id == party_id))
    party = result.scalar_one_or_none()
    if not party:
        raise HTTPException(status_code=404, detail="Party not found")
    return party


@router.patch("/{party_id}", response_model=PartyResponse)
async def update_party(
    party_id: uuid.UUID,
    body: PartyUpdate,
    user: PartyUser = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Party).where(Party.id == party_id))
    party = result.scalar_one_or_none()
    if not party:
        raise HTTPException(status_code=404, detail="Party not found")

    if body.name is not None:
        party.name = body.name
    if body.short_name is not None:
        party.short_name = body.short_name
    if body.registration_number is not None:
        party.registration_number = body.registration_number
    if body.contact_email is not None:
        party.contact_email_encrypted = encrypt_string(body.contact_email)
    if body.status is not None:
        party.status = body.status

    await db.commit()
    await db.refresh(party)
    return party


@router.post(
    "/{party_id}/users",
    response_model=PartyUserResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_party_user(
    party_id: uuid.UUID,
    body: PartyUserCreate,
    user: PartyUser = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """Add a user to a party (admin only)."""
    # Verify party exists
    party_result = await db.execute(select(Party).where(Party.id == party_id))
    if not party_result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Party not found")

    # Check duplicate username
    existing = await db.execute(
        select(PartyUser).where(PartyUser.username == body.username)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Username already taken"
        )

    new_user = PartyUser(
        party_id=party_id,
        username=body.username,
        email_encrypted=encrypt_string(body.email),
        hashed_password=hash_password(body.password),
        role=body.role,
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user
