"""EC user management endpoints: list users, change email, trigger password reset."""

import hashlib
import logging
import secrets
import uuid
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import hash_password, require_electoral_commission
from app.core.config import settings
from app.core.database import get_db
from app.models.party import Party, PartyUser, UserRole
from app.services.encryption import decrypt_string, encrypt_string


from app.services.email_sender import (
    send_email_changed_notification,
    send_password_reset_email,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ec", tags=["ec_user_management"])


class EmailUpdateRequest(BaseModel):
    email: str


class CreateCandidateRequest(BaseModel):
    username: str
    email: str
    password: str
    promoter_statement: str | None = None


@router.get("/users")
async def ec_list_users(
    user: PartyUser = Depends(require_electoral_commission),
    db: AsyncSession = Depends(get_db),
):
    """List all party users with decrypted emails (EC only)."""
    result = await db.execute(
        select(PartyUser, Party.name.label("party_name"))
        .join(Party, Party.id == PartyUser.party_id)
        .order_by(Party.name, PartyUser.username)
    )
    rows = result.all()

    users = []
    for row in rows:
        u = row.PartyUser
        try:
            email = decrypt_string(u.email_encrypted)
        except Exception:
            email = "(decryption error)"

        users.append(
            {
                "id": str(u.id),
                "username": u.username,
                "email": email,
                "role": u.role.value,
                "party_name": row.party_name,
                "is_active": u.is_active,
                "mfa_enabled": u.mfa_enabled,
                "email_verified": u.email_verified_for_processing,
                "last_login": u.last_login.isoformat() if u.last_login else None,
                "created_at": u.created_at.isoformat(),
            }
        )
    return users


@router.patch("/users/{user_id}/email")
async def ec_update_user_email(
    user_id: uuid.UUID,
    body: EmailUpdateRequest,
    user: PartyUser = Depends(require_electoral_commission),
    db: AsyncSession = Depends(get_db),
):
    """Change a user's email address (EC only). Notifies both addresses."""
    result = await db.execute(select(PartyUser).where(PartyUser.id == user_id))
    target = result.scalar_one_or_none()
    if not target:
        raise HTTPException(status_code=404, detail="User not found")

    # Safety: cannot modify other EC accounts
    if target.role == UserRole.ELECTORAL_COMMISSION:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot modify Electoral Commission accounts",
        )

    # Decrypt old email for notification
    try:
        old_email = decrypt_string(target.email_encrypted)
    except Exception:
        old_email = None

    new_email = body.email
    target.email_encrypted = encrypt_string(new_email)
    target.email_verified_for_processing = False
    await db.commit()

    # Notify both addresses (best-effort, don't fail the request)
    if old_email:
        try:
            await send_email_changed_notification(old_email, new_email)
        except Exception:
            logger.warning("Failed to send email change notifications")

    return {"detail": "Email updated", "email": new_email}


@router.post("/users/{user_id}/reset-password")
async def ec_trigger_password_reset(
    user_id: uuid.UUID,
    user: PartyUser = Depends(require_electoral_commission),
    db: AsyncSession = Depends(get_db),
):
    """Trigger a password reset email for a user (EC only)."""
    result = await db.execute(select(PartyUser).where(PartyUser.id == user_id))
    target = result.scalar_one_or_none()
    if not target:
        raise HTTPException(status_code=404, detail="User not found")

    # Safety: cannot reset other EC accounts
    if target.role == UserRole.ELECTORAL_COMMISSION:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot reset Electoral Commission accounts",
        )

    # Generate token (same pattern as email_processor._generate_verification_token)
    token = secrets.token_urlsafe(32)
    token_hash = hashlib.sha256(token.encode()).hexdigest()

    target.password_reset_token_hash = token_hash
    target.password_reset_expires = datetime.now(timezone.utc) + timedelta(
        minutes=settings.PASSWORD_RESET_EXPIRE_MINUTES
    )
    await db.commit()

    # Send the reset email
    try:
        recipient = decrypt_string(target.email_encrypted)
        await send_password_reset_email(recipient, token)
    except Exception:
        logger.warning("Failed to send password reset email for user %s", user_id)
        return {
            "detail": "Reset token created but email delivery failed. "
            "Check SMTP configuration.",
        }

    return {"detail": "Password reset email sent"}


@router.post("/candidates", status_code=status.HTTP_201_CREATED)
async def ec_create_candidate(
    body: CreateCandidateRequest,
    party_id: uuid.UUID | None = None,
    user: PartyUser = Depends(require_electoral_commission),
    db: AsyncSession = Depends(get_db),
):
    """Create a candidate account in any party (EC only).

    If party_id is not provided, defaults to the 'Independent Candidates' party.
    """
    if party_id:
        party_result = await db.execute(select(Party).where(Party.id == party_id))
    else:
        party_result = await db.execute(
            select(Party).where(Party.short_name == "Independent")
        )
    party = party_result.scalar_one_or_none()
    if not party:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Party not found. Ensure 'Independent Candidates' party exists.",
        )

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
        party_id=party.id,
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
        "party_name": party.name,
        "detail": "Candidate account created",
    }
