"""Electoral Commission dashboard API endpoints."""

import uuid
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import Response
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import require_electoral_commission
from app.core.database import get_db
from app.models.asset import Asset, AssetStatus
from app.models.geo_stats import VerificationGeoStat
from app.models.party import Party, PartyUser
from app.models.verification import VerificationLog, VerificationResult
from app.services.encryption import decrypt_dek, decrypt_data
from app.services.storage import retrieve_blob

router = APIRouter(prefix="/ec", tags=["electoral_commission"])


@router.get("/parties")
async def ec_list_parties(
    user: PartyUser = Depends(require_electoral_commission),
    db: AsyncSession = Depends(get_db),
):
    """List all parties with asset counts."""
    # Get parties
    party_result = await db.execute(
        select(Party).order_by(Party.name)
    )
    parties = party_result.scalars().all()

    result = []
    for p in parties:
        # Count assets
        total = await db.execute(
            select(func.count(Asset.id)).where(Asset.party_id == p.id)
        )
        active = await db.execute(
            select(func.count(Asset.id)).where(
                Asset.party_id == p.id, Asset.status == AssetStatus.ACTIVE
            )
        )
        revoked = await db.execute(
            select(func.count(Asset.id)).where(
                Asset.party_id == p.id, Asset.status == AssetStatus.REVOKED
            )
        )
        result.append(
            {
                "id": str(p.id),
                "name": p.name,
                "short_name": p.short_name,
                "status": p.status.value,
                "has_promoter_statement": bool(p.promoter_statement),
                "asset_count": total.scalar() or 0,
                "active_count": active.scalar() or 0,
                "revoked_count": revoked.scalar() or 0,
            }
        )
    return result


@router.get("/stats")
async def ec_verification_stats(
    days: int = Query(30, ge=1, le=365),
    user: PartyUser = Depends(require_electoral_commission),
    db: AsyncSession = Depends(get_db),
):
    """Aggregate verification statistics."""
    since = datetime.now(timezone.utc) - timedelta(days=days)

    total = await db.execute(
        select(func.count(VerificationLog.id)).where(
            VerificationLog.created_at >= since
        )
    )
    total_count = total.scalar() or 0

    verified = await db.execute(
        select(func.count(VerificationLog.id)).where(
            VerificationLog.created_at >= since,
            VerificationLog.result == VerificationResult.VERIFIED,
        )
    )
    verified_count = verified.scalar() or 0

    # Daily trend
    daily = await db.execute(
        select(
            func.date_trunc("day", VerificationLog.created_at).label("day"),
            func.count(VerificationLog.id).label("total"),
        )
        .where(VerificationLog.created_at >= since)
        .group_by(func.date_trunc("day", VerificationLog.created_at))
        .order_by(func.date_trunc("day", VerificationLog.created_at))
    )

    return {
        "period_days": days,
        "total_verifications": total_count,
        "verified_count": verified_count,
        "unverified_count": total_count - verified_count,
        "verification_rate": (
            round(verified_count / total_count * 100, 1) if total_count > 0 else 0
        ),
        "daily_trend": [
            {"date": str(r.day.date()) if r.day else "", "total": r.total}
            for r in daily.all()
        ],
    }


@router.get("/geo")
async def ec_geo_stats(
    days: int = Query(30, ge=1, le=365),
    user: PartyUser = Depends(require_electoral_commission),
    db: AsyncSession = Depends(get_db),
):
    """Geographic aggregate verification data."""
    since = datetime.now(timezone.utc) - timedelta(days=days)

    result = await db.execute(
        select(
            VerificationGeoStat.region,
            VerificationGeoStat.country,
            func.sum(VerificationGeoStat.verification_count).label("total"),
        )
        .where(VerificationGeoStat.date >= since.date())
        .group_by(VerificationGeoStat.region, VerificationGeoStat.country)
        .order_by(func.sum(VerificationGeoStat.verification_count).desc())
    )

    return [
        {"region": r.region, "country": r.country, "count": r.total}
        for r in result.all()
    ]


@router.get("/images")
async def ec_browse_images(
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=200),
    party_id: str | None = Query(None),
    user: PartyUser = Depends(require_electoral_commission),
    db: AsyncSession = Depends(get_db),
):
    """Browse registered images across all parties (read-only)."""
    query = (
        select(Asset, Party.name.label("party_name"), Party.short_name.label("party_short_name"))
        .join(Party, Party.id == Asset.party_id)
        .order_by(Asset.created_at.desc())
        .offset((page - 1) * per_page)
        .limit(per_page)
    )
    if party_id:
        query = query.where(Asset.party_id == uuid.UUID(party_id))

    result = await db.execute(query)
    rows = result.all()
    return [
        {
            "id": str(r.Asset.id),
            "party_name": r.party_name,
            "party_short_name": r.party_short_name,
            "verification_id": r.Asset.verification_id,
            "mime_type": r.Asset.mime_type,
            "file_size": r.Asset.file_size,
            "status": r.Asset.status.value,
            "created_at": r.Asset.created_at.isoformat(),
            "thumbnail_url": (
                f"/api/v1/ec/images/{r.Asset.id}/thumbnail"
                if r.Asset.thumbnail_storage_key
                else None
            ),
        }
        for r in rows
    ]


@router.get("/images/{asset_id}/thumbnail")
async def ec_get_thumbnail(
    asset_id: uuid.UUID,
    user: PartyUser = Depends(require_electoral_commission),
    db: AsyncSession = Depends(get_db),
):
    """Get a thumbnail for EC browsing (read-only)."""
    result = await db.execute(select(Asset).where(Asset.id == asset_id))
    asset = result.scalar_one_or_none()
    if not asset or not asset.thumbnail_storage_key:
        raise HTTPException(status_code=404, detail="Thumbnail not found")

    thumb_bytes = await retrieve_blob(asset.thumbnail_storage_key)
    return Response(content=thumb_bytes, media_type="image/jpeg")


@router.get("/images/{asset_id}/download/{version}")
async def ec_download_image(
    asset_id: uuid.UUID,
    version: str,
    user: PartyUser = Depends(require_electoral_commission),
    db: AsyncSession = Depends(get_db),
):
    """Download an asset version (EC only, any party)."""
    if version not in ("original", "promoter", "badge"):
        raise HTTPException(
            status_code=400,
            detail="Version must be: original, promoter, badge",
        )

    result = await db.execute(select(Asset).where(Asset.id == asset_id))
    asset = result.scalar_one_or_none()
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")

    if version == "original":
        storage_key_parts = asset.encrypted_storage_key.split("|")
        storage_key = storage_key_parts[0]
        encrypted_dek_b64 = storage_key_parts[1]
        encrypted_blob = await retrieve_blob(storage_key)
        dek = decrypt_dek(encrypted_dek_b64)
        nonce = bytes.fromhex(asset.encryption_iv)
        blob_bytes = decrypt_data(encrypted_blob, dek, nonce)
    elif version == "promoter":
        if not asset.promoter_storage_key:
            raise HTTPException(status_code=404, detail="No promoter version available")
        blob_bytes = await retrieve_blob(asset.promoter_storage_key)
    elif version == "badge":
        if not asset.badge_storage_key:
            raise HTTPException(status_code=404, detail="No badge version available")
        blob_bytes = await retrieve_blob(asset.badge_storage_key)

    return Response(
        content=blob_bytes,
        media_type="image/png",
        headers={
            "Content-Disposition": (
                f'attachment; filename="{version}_{asset.verification_id}.png"'
            )
        },
    )
