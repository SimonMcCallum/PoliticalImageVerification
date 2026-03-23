"""Public verification endpoints - no authentication required."""

import asyncio
import hashlib
import logging
from datetime import date

from fastapi import APIRouter, Depends, File, Request, UploadFile
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.models.asset import Asset, AssetStatus
from app.models.geo_stats import VerificationGeoStat
from app.models.party import Party
from app.models.verification import MatchType, VerificationLog, VerificationResult
from app.schemas.verification import (
    HashVerifyRequest,
    VerificationByIdResponse,
    VerificationResponse,
)
from app.services.hashing import (
    compute_all_hashes,
    pdq_match,
    phash_match,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/verify", tags=["verification"])


def _hash_ip(request: Request) -> str:
    client_ip = request.client.host if request.client else "unknown"
    return hashlib.sha256(client_ip.encode()).hexdigest()


async def _find_match(
    db: AsyncSession,
    sha256: str | None = None,
    pdq_hash: str | None = None,
    phash: str | None = None,
) -> tuple[Asset | None, MatchType, int | None, int | None, float]:
    """Search for matching assets using hash comparison.
    Returns (asset, match_type, pdq_distance, phash_distance, confidence).
    """
    # 1. Try exact SHA-256 match first (fastest)
    if sha256:
        result = await db.execute(
            select(Asset).where(
                Asset.sha256_hash == sha256,
                Asset.status == AssetStatus.ACTIVE,
            )
        )
        asset = result.scalar_one_or_none()
        if asset:
            return asset, MatchType.EXACT, None, None, 1.0

    # 2. Try PDQ perceptual match
    if pdq_hash:
        result = await db.execute(
            select(Asset).where(Asset.status == AssetStatus.ACTIVE)
        )
        assets = result.scalars().all()
        best_match = None
        best_distance = 256
        for asset in assets:
            is_match, distance = pdq_match(pdq_hash, asset.pdq_hash)
            if is_match and distance < best_distance:
                best_distance = distance
                best_match = asset

        if best_match:
            confidence = 1.0 - (best_distance / settings.PDQ_MATCH_THRESHOLD)
            return (
                best_match,
                MatchType.PERCEPTUAL,
                best_distance,
                None,
                max(0.5, confidence),
            )

    # 3. Try pHash fallback
    if phash:
        result = await db.execute(
            select(Asset).where(Asset.status == AssetStatus.ACTIVE)
        )
        assets = result.scalars().all()
        best_match = None
        best_distance = 64
        for asset in assets:
            is_match, distance = phash_match(phash, asset.phash)
            if is_match and distance < best_distance:
                best_distance = distance
                best_match = asset

        if best_match:
            confidence = 1.0 - (best_distance / settings.PHASH_MATCH_THRESHOLD)
            return (
                best_match,
                MatchType.PERCEPTUAL,
                None,
                best_distance,
                max(0.4, confidence),
            )

    return None, MatchType.NONE, None, None, 0.0


async def _build_response(
    asset: Asset | None,
    match_type: MatchType,
    pdq_distance: int | None,
    phash_distance: int | None,
    confidence: float,
    db: AsyncSession,
) -> VerificationResponse:
    if asset:
        party_result = await db.execute(
            select(Party).where(Party.id == asset.party_id)
        )
        party = party_result.scalar_one_or_none()
        return VerificationResponse(
            verified=True,
            result=VerificationResult.VERIFIED,
            match_type=match_type,
            confidence=confidence,
            party={
                "name": party.name if party else "Unknown",
                "short_name": party.short_name if party else "Unknown",
            },
            asset_id=asset.id,
            verification_id=asset.verification_id,
            registered_date=asset.created_at,
            pdq_distance=pdq_distance,
            phash_distance=phash_distance,
        )
    return VerificationResponse(
        verified=False,
        result=VerificationResult.UNVERIFIED,
        match_type=MatchType.NONE,
        confidence=0.0,
    )


async def _record_geo_stat(request: Request, db: AsyncSession) -> None:
    """Record geographic stats for this verification request.

    IP is resolved in memory and only the aggregate count is persisted.
    The IP address is NEVER stored.
    """
    try:
        from app.services.geolocation import resolve_location

        client_ip = request.client.host if request.client else None
        if not client_ip:
            return

        region, country = await resolve_location(client_ip)
        today = date.today()

        result = await db.execute(
            select(VerificationGeoStat).where(
                VerificationGeoStat.date == today,
                VerificationGeoStat.region == region,
                VerificationGeoStat.country == country,
            )
        )
        stat = result.scalar_one_or_none()
        if stat:
            stat.verification_count += 1
        else:
            stat = VerificationGeoStat(
                date=today,
                region=region,
                country=country,
                verification_count=1,
            )
            db.add(stat)
    except Exception:
        logger.debug("Geo stat recording failed (non-fatal)")


@router.post("/image", response_model=VerificationResponse)
async def verify_image(
    request: Request,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
):
    """Upload an image to check if it's registered by any party."""
    image_bytes = await file.read()
    if len(image_bytes) == 0:
        return VerificationResponse(
            verified=False,
            result=VerificationResult.ERROR,
            match_type=MatchType.NONE,
            confidence=0.0,
        )

    hashes = compute_all_hashes(image_bytes)
    asset, match_type, pdq_dist, phash_dist, confidence = await _find_match(
        db,
        sha256=hashes["sha256"],
        pdq_hash=hashes["pdq_hash"],
        phash=hashes["phash"],
    )

    # OCR-based promoter detection (only when hash matching fails)
    promoter_detected = False
    promoter_party_name = None
    if not asset:
        try:
            from app.services.ocr import find_promoter_across_parties

            party_result = await db.execute(
                select(Party).where(Party.promoter_statement.isnot(None))
            )
            parties_with_statements = [
                (str(p.id), p.name, p.promoter_statement)
                for p in party_result.scalars().all()
            ]
            if parties_with_statements:
                ocr_result = await asyncio.get_event_loop().run_in_executor(
                    None,
                    find_promoter_across_parties,
                    image_bytes,
                    parties_with_statements,
                )
                if ocr_result.get("found"):
                    promoter_detected = True
                    promoter_party_name = ocr_result.get("party_name")
        except Exception:
            pass  # OCR failure is non-fatal

    # Record geographic stats (privacy-first: only aggregate counts)
    await _record_geo_stat(request, db)

    # Log the verification attempt
    log_entry = VerificationLog(
        asset_id=asset.id if asset else None,
        match_type=match_type,
        pdq_distance=pdq_dist,
        phash_distance=phash_dist,
        source_ip_hash=_hash_ip(request),
        result=(
            VerificationResult.VERIFIED if asset else VerificationResult.UNVERIFIED
        ),
    )
    db.add(log_entry)
    await db.commit()

    response = await _build_response(
        asset, match_type, pdq_dist, phash_dist, confidence, db
    )

    # Augment response with OCR data
    if promoter_detected and not asset:
        response.promoter_detected = True
        response.promoter_party_name = promoter_party_name

    return response


@router.post("/hash", response_model=VerificationResponse)
async def verify_hash(
    request: Request,
    body: HashVerifyRequest,
    db: AsyncSession = Depends(get_db),
):
    """Verify using pre-computed hash values."""
    if not any([body.sha256, body.pdq, body.phash]):
        return VerificationResponse(
            verified=False,
            result=VerificationResult.ERROR,
            match_type=MatchType.NONE,
            confidence=0.0,
        )

    asset, match_type, pdq_dist, phash_dist, confidence = await _find_match(
        db, sha256=body.sha256, pdq_hash=body.pdq, phash=body.phash
    )

    # Record geographic stats
    await _record_geo_stat(request, db)

    log_entry = VerificationLog(
        asset_id=asset.id if asset else None,
        match_type=match_type,
        pdq_distance=pdq_dist,
        phash_distance=phash_dist,
        source_ip_hash=_hash_ip(request),
        result=(
            VerificationResult.VERIFIED if asset else VerificationResult.UNVERIFIED
        ),
    )
    db.add(log_entry)
    await db.commit()

    return await _build_response(asset, match_type, pdq_dist, phash_dist, confidence, db)


@router.get("/{verification_id}", response_model=VerificationByIdResponse)
async def verify_by_id(
    verification_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Look up a verification by its short ID (from QR code scan)."""
    result = await db.execute(
        select(Asset).where(Asset.verification_id == verification_id)
    )
    asset = result.scalar_one_or_none()

    if not asset or asset.status != AssetStatus.ACTIVE:
        return VerificationByIdResponse(
            verified=False,
            verification_id=verification_id,
            status="not_found" if not asset else asset.status.value,
        )

    party_result = await db.execute(select(Party).where(Party.id == asset.party_id))
    party = party_result.scalar_one_or_none()

    return VerificationByIdResponse(
        verified=True,
        party_name=party.name if party else None,
        party_short_name=party.short_name if party else None,
        registered_date=asset.created_at,
        status=asset.status.value,
        verification_id=verification_id,
    )
