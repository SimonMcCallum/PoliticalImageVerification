"""Authentication endpoints: login, MFA setup."""

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import (
    create_access_token,
    generate_mfa_secret,
    get_current_user,
    get_mfa_provisioning_uri,
    hash_password,
    verify_mfa_code,
    verify_password,
)
from app.core.database import get_db
from app.models.party import PartyUser
from app.schemas.auth import LoginRequest, MFASetupResponse, TokenResponse
from app.services.encryption import decrypt_string, encrypt_string

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
async def login(body: LoginRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(PartyUser).where(PartyUser.username == body.username)
    )
    user = result.scalar_one_or_none()
    if not user or not verify_password(body.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is disabled",
        )

    # MFA check
    if user.mfa_enabled:
        if not body.mfa_code:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="MFA code required",
            )
        if not verify_mfa_code(user.mfa_secret_encrypted, body.mfa_code):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid MFA code",
            )

    # Update last login
    user.last_login = datetime.now(timezone.utc)
    await db.commit()

    token = create_access_token(user.id, user.party_id, user.role.value)
    return TokenResponse(access_token=token)


@router.post("/mfa/setup", response_model=MFASetupResponse)
async def setup_mfa(
    user: PartyUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if user.mfa_enabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="MFA is already enabled",
        )

    secret = generate_mfa_secret()
    provisioning_uri = get_mfa_provisioning_uri(secret, user.username)

    # Store encrypted secret (not yet enabled until confirmed)
    user.mfa_secret_encrypted = encrypt_string(secret)
    await db.commit()

    return MFASetupResponse(secret=secret, provisioning_uri=provisioning_uri)


@router.post("/mfa/confirm")
async def confirm_mfa(
    code: str,
    user: PartyUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if not user.mfa_secret_encrypted:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Run MFA setup first",
        )
    if not verify_mfa_code(user.mfa_secret_encrypted, code):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid MFA code",
        )

    user.mfa_enabled = True
    await db.commit()
    return {"detail": "MFA enabled successfully"}
