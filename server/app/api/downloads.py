"""Download endpoints: authenticated and shareable links."""

import hashlib
import secrets
import uuid
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import Response
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_current_user, require_submitter
from app.core.config import settings
from app.core.database import get_db
from app.models.asset import Asset
from app.models.party import PartyUser
from app.models.share_link import ShareLink
from app.services.encryption import decrypt_dek, decrypt_data
from app.services.storage import retrieve_blob

router = APIRouter(tags=["downloads"])


async def _get_asset_version(asset: Asset, version: str) -> bytes:
    """Retrieve the specified version of an asset."""
    if version == "original":
        storage_key_parts = asset.encrypted_storage_key.split("|")
        storage_key = storage_key_parts[0]
        encrypted_dek_b64 = storage_key_parts[1]
        encrypted_blob = await retrieve_blob(storage_key)
        dek = decrypt_dek(encrypted_dek_b64)
        nonce = bytes.fromhex(asset.encryption_iv)
        return decrypt_data(encrypted_blob, dek, nonce)
    elif version == "promoter":
        if not asset.promoter_storage_key:
            raise HTTPException(
                status_code=404, detail="No promoter version available"
            )
        return await retrieve_blob(asset.promoter_storage_key)
    elif version == "badge":
        if not asset.badge_storage_key:
            raise HTTPException(status_code=404, detail="No badge version available")
        return await retrieve_blob(asset.badge_storage_key)
    else:
        raise HTTPException(status_code=400, detail="Invalid version")


# --- Authenticated downloads ---


@router.get("/assets/{asset_id}/download/{version}")
async def download_asset_authenticated(
    asset_id: uuid.UUID,
    version: str,
    user: PartyUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Download an asset version (authenticated party member).

    Version must be one of: original, promoter, badge
    """
    if version not in ("original", "promoter", "badge"):
        raise HTTPException(
            status_code=400,
            detail="Version must be: original, promoter, badge",
        )

    result = await db.execute(
        select(Asset).where(Asset.id == asset_id, Asset.party_id == user.party_id)
    )
    asset = result.scalar_one_or_none()
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")

    blob_bytes = await _get_asset_version(asset, version)
    return Response(
        content=blob_bytes,
        media_type="image/png",
        headers={
            "Content-Disposition": (
                f'attachment; filename="{version}_{asset.verification_id}.png"'
            )
        },
    )


# --- Shareable links ---


@router.post("/assets/{asset_id}/share")
async def create_share_link(
    asset_id: uuid.UUID,
    version: str = Query("promoter", pattern="^(original|promoter|badge)$"),
    expire_hours: int = Query(72, ge=1, le=720),
    max_downloads: int | None = Query(None, ge=1),
    user: PartyUser = Depends(require_submitter),
    db: AsyncSession = Depends(get_db),
):
    """Create a shareable download link for an asset."""
    result = await db.execute(
        select(Asset).where(Asset.id == asset_id, Asset.party_id == user.party_id)
    )
    asset = result.scalar_one_or_none()
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")

    token = secrets.token_urlsafe(32)
    token_hash = hashlib.sha256(token.encode()).hexdigest()

    share = ShareLink(
        asset_id=asset.id,
        token_hash=token_hash,
        created_by=user.id,
        version=version,
        expires_at=datetime.now(timezone.utc) + timedelta(hours=expire_hours),
        max_downloads=max_downloads,
    )
    db.add(share)
    await db.commit()
    await db.refresh(share)

    base_url = settings.VERIFICATION_BASE_URL.rstrip("/")
    download_url = f"{base_url}/download/{token}"
    return {
        "id": str(share.id),
        "download_url": download_url,
        "token": token,
        "version": version,
        "expires_at": share.expires_at.isoformat(),
        "max_downloads": max_downloads,
    }


@router.get("/assets/{asset_id}/shares")
async def list_share_links(
    asset_id: uuid.UUID,
    user: PartyUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List active share links for an asset."""
    # Verify asset ownership
    asset_result = await db.execute(
        select(Asset).where(Asset.id == asset_id, Asset.party_id == user.party_id)
    )
    if not asset_result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Asset not found")

    result = await db.execute(
        select(ShareLink)
        .where(ShareLink.asset_id == asset_id, ShareLink.is_active == True)
        .order_by(ShareLink.created_at.desc())
    )
    shares = result.scalars().all()
    return [
        {
            "id": str(s.id),
            "version": s.version,
            "expires_at": s.expires_at.isoformat(),
            "download_count": s.download_count,
            "max_downloads": s.max_downloads,
            "created_at": s.created_at.isoformat(),
        }
        for s in shares
    ]


@router.delete("/share/{share_id}")
async def revoke_share_link(
    share_id: uuid.UUID,
    user: PartyUser = Depends(require_submitter),
    db: AsyncSession = Depends(get_db),
):
    """Revoke a shareable link."""
    result = await db.execute(
        select(ShareLink).where(ShareLink.id == share_id)
    )
    share = result.scalar_one_or_none()
    if not share:
        raise HTTPException(status_code=404, detail="Share link not found")

    # Verify ownership via asset's party
    asset_result = await db.execute(
        select(Asset).where(
            Asset.id == share.asset_id, Asset.party_id == user.party_id
        )
    )
    if not asset_result.scalar_one_or_none():
        raise HTTPException(status_code=403, detail="Not authorized")

    share.is_active = False
    await db.commit()
    return {"detail": "Share link revoked"}


# --- Public download via token (no auth) ---


@router.get("/download/{token}")
async def download_via_share_link(
    token: str,
    db: AsyncSession = Depends(get_db),
):
    """Public download via shareable link (no auth required)."""
    token_hash = hashlib.sha256(token.encode()).hexdigest()
    result = await db.execute(
        select(ShareLink).where(ShareLink.token_hash == token_hash)
    )
    share = result.scalar_one_or_none()

    if not share or not share.is_active:
        raise HTTPException(status_code=404, detail="Link not found or revoked")

    if share.expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=410, detail="Link has expired")

    if share.max_downloads and share.download_count >= share.max_downloads:
        raise HTTPException(status_code=410, detail="Download limit reached")

    asset_result = await db.execute(
        select(Asset).where(Asset.id == share.asset_id)
    )
    asset = asset_result.scalar_one_or_none()
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")

    blob_bytes = await _get_asset_version(asset, share.version)

    # Increment download count
    share.download_count += 1
    await db.commit()

    return Response(
        content=blob_bytes,
        media_type="image/png",
        headers={
            "Content-Disposition": (
                f'attachment; filename="{share.version}_{asset.verification_id}.png"'
            )
        },
    )
