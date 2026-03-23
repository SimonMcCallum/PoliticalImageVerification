"""Party admin endpoints: manage users within own party."""

import hashlib
import logging
import secrets
import uuid
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import hash_password, require_party_admin
from app.core.config import settings
from app.core.database import get_db
from app.models.party import Party, PartyUser, UserRole
from app.services.encryption import decrypt_string, encrypt_string
from app.services.email_sender import (
    send_email_changed_notification,
    send_password_reset_email,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/parties", tags=["party_admin"])


class CreateCandidateRequest(BaseModel):
    username: str
    email: str
    password: str
    promoter_statement: str | None = None


class EmailUpdateRequest(BaseModel):
    email: str


class ActiveUpdateRequest(BaseModel):
    is_active: bool


@router.get("/{party_id}/members")
async def list_party_members(
    party_id: uuid.UUID,
    user: PartyUser = Depends(require_party_admin),
    db: AsyncSession = Depends(get_db),
):
    """List all users in a party (party admin only, own party)."""
    if user.party_id != party_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorised for this party",
        )

    result = await db.execute(
        select(PartyUser)
        .where(PartyUser.party_id == party_id)
        .order_by(PartyUser.username)
    )
    members = result.scalars().all()

    out = []
    for m in members:
        try:
            email = decrypt_string(m.email_encrypted)
        except Exception:
            email = "(decryption error)"
        out.append({
            "id": str(m.id),
            "username": m.username,
            "email": email,
            "role": m.role.value,
            "is_active": m.is_active,
            "has_promoter_statement": m.promoter_statement is not None,
            "last_login": m.last_login.isoformat() if m.last_login else None,
            "created_at": m.created_at.isoformat(),
        })
    return out


@router.post("/{party_id}/candidates", status_code=status.HTTP_201_CREATED)
async def create_candidate(
    party_id: uuid.UUID,
    body: CreateCandidateRequest,
    user: PartyUser = Depends(require_party_admin),
    db: AsyncSession = Depends(get_db),
):
    """Create a candidate account within the party (party admin only)."""
    if user.party_id != party_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorised for this party",
        )

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
            status_code=status.HTTP_409_CONFLICT,
            detail="Username already taken",
        )

    if len(body.password) < 8:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 8 characters",
        )

    now = datetime.now(timezone.utc)
    new_user = PartyUser(
        party_id=party_id,
        username=body.username,
        email_encrypted=encrypt_string(body.email),
        hashed_password=hash_password(body.password),
        role=UserRole.CANDIDATE,
        promoter_statement=body.promoter_statement if body.promoter_statement else None,
        promoter_statement_updated_at=now if body.promoter_statement else None,
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    return {
        "id": str(new_user.id),
        "username": new_user.username,
        "role": new_user.role.value,
        "party_id": str(new_user.party_id),
        "detail": "Candidate account created",
    }


@router.patch("/{party_id}/members/{member_id}/email")
async def update_member_email(
    party_id: uuid.UUID,
    member_id: uuid.UUID,
    body: EmailUpdateRequest,
    user: PartyUser = Depends(require_party_admin),
    db: AsyncSession = Depends(get_db),
):
    """Change a member's email address (party admin only, own party)."""
    if user.party_id != party_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorised for this party",
        )

    result = await db.execute(
        select(PartyUser).where(
            PartyUser.id == member_id,
            PartyUser.party_id == party_id,
        )
    )
    target = result.scalar_one_or_none()
    if not target:
        raise HTTPException(status_code=404, detail="Member not found")

    # Cannot modify other admins or EC accounts
    if target.role in (UserRole.ADMIN, UserRole.ELECTORAL_COMMISSION) and target.id != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot modify other admin accounts",
        )

    try:
        old_email = decrypt_string(target.email_encrypted)
    except Exception:
        old_email = None

    new_email = body.email
    target.email_encrypted = encrypt_string(new_email)
    target.email_verified_for_processing = False
    await db.commit()

    if old_email:
        try:
            await send_email_changed_notification(old_email, new_email)
        except Exception:
            logger.warning("Failed to send email change notification")

    return {"detail": "Email updated", "email": new_email}


@router.post("/{party_id}/members/{member_id}/reset-password")
async def trigger_member_password_reset(
    party_id: uuid.UUID,
    member_id: uuid.UUID,
    user: PartyUser = Depends(require_party_admin),
    db: AsyncSession = Depends(get_db),
):
    """Trigger a password reset for a party member (party admin only, own party)."""
    if user.party_id != party_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorised for this party",
        )

    result = await db.execute(
        select(PartyUser).where(
            PartyUser.id == member_id,
            PartyUser.party_id == party_id,
        )
    )
    target = result.scalar_one_or_none()
    if not target:
        raise HTTPException(status_code=404, detail="Member not found")

    if target.role in (UserRole.ADMIN, UserRole.ELECTORAL_COMMISSION) and target.id != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot reset other admin accounts",
        )

    token = secrets.token_urlsafe(32)
    token_hash = hashlib.sha256(token.encode()).hexdigest()

    target.password_reset_token_hash = token_hash
    target.password_reset_expires = datetime.now(timezone.utc) + timedelta(
        minutes=settings.PASSWORD_RESET_EXPIRE_MINUTES
    )
    await db.commit()

    try:
        recipient = decrypt_string(target.email_encrypted)
        await send_password_reset_email(recipient, token)
    except Exception:
        logger.warning("Failed to send password reset email for user %s", member_id)
        return {"detail": "Reset token created but email delivery failed."}

    return {"detail": "Password reset email sent"}


@router.patch("/{party_id}/members/{member_id}/active")
async def toggle_member_active(
    party_id: uuid.UUID,
    member_id: uuid.UUID,
    body: ActiveUpdateRequest,
    user: PartyUser = Depends(require_party_admin),
    db: AsyncSession = Depends(get_db),
):
    """Activate or deactivate a party member (party admin only, own party)."""
    if user.party_id != party_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorised for this party",
        )

    result = await db.execute(
        select(PartyUser).where(
            PartyUser.id == member_id,
            PartyUser.party_id == party_id,
        )
    )
    target = result.scalar_one_or_none()
    if not target:
        raise HTTPException(status_code=404, detail="Member not found")

    if target.role in (UserRole.ADMIN, UserRole.ELECTORAL_COMMISSION) and target.id != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot modify other admin accounts",
        )

    target.is_active = body.is_active
    await db.commit()

    return {
        "detail": f"User {'activated' if body.is_active else 'deactivated'}",
        "is_active": target.is_active,
    }
