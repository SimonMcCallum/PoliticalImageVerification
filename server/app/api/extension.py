"""Public extension endpoints: potential-breach reports, user flags,
and the bloom-filter snapshot used by the extension for local lookups.

No authentication is required (the extension runs anonymously on user
devices). Requests are rate-limited by hashed source IP. De-duplication
on reports is by perceptual hash (``pdq`` preferred, falling back to
``sha256``) so repeated observations of the same image raise the
``observed_count`` rather than creating new rows.
"""

import hashlib
import logging
import time
from collections import defaultdict, deque

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import Response
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.models.asset import Asset, AssetStatus
from app.models.extension import ExtensionFlag, ExtensionReport, FlagStatus
from app.schemas.extension import (
    ExtensionFlagRequest,
    ExtensionFlagResponse,
    ExtensionReportRequest,
    ExtensionReportResponse,
)
from app.services.bloom import BloomFilter

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/extension", tags=["extension"])


# --------------------------------------------------------------------------
# Simple in-process rate limiter. This is fine for a single-instance
# deployment. For multi-instance deployment behind a load balancer,
# swap this for nginx-level rate limiting or a shared Redis-backed
# counter.
# --------------------------------------------------------------------------

_rate_buckets: dict[str, deque[float]] = defaultdict(deque)


def _rate_limit(key: str, per_minute: int) -> bool:
    """Return True if the request is within the allowed rate, False otherwise."""
    now = time.time()
    window_start = now - 60
    bucket = _rate_buckets[key]
    while bucket and bucket[0] < window_start:
        bucket.popleft()
    if len(bucket) >= per_minute:
        return False
    bucket.append(now)
    return True


def _hash_ip(request: Request) -> str:
    client_ip = request.client.host if request.client else "unknown"
    return hashlib.sha256(client_ip.encode()).hexdigest()


# --------------------------------------------------------------------------
# Endpoints
# --------------------------------------------------------------------------


@router.post("/report", response_model=ExtensionReportResponse)
async def report_unregistered(
    request: Request,
    body: ExtensionReportRequest,
    db: AsyncSession = Depends(get_db),
):
    """Record an extension-observed image that carries a promoter statement
    but did not match the register. Reports are de-duplicated by perceptual
    hash, so the same image being reported many times increases the
    ``observed_count`` on a single row rather than creating duplicates.
    """
    if not any([body.sha256, body.pdq, body.phash]):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one of sha256, pdq, phash is required",
        )

    ip_hash = _hash_ip(request)
    if not _rate_limit(
        f"report:{ip_hash}", settings.RATE_LIMIT_EXTENSION_REPORT_PER_MINUTE
    ):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded",
        )

    # De-duplicate: prefer pdq, then sha256, then phash.
    existing: ExtensionReport | None = None
    if body.pdq:
        result = await db.execute(
            select(ExtensionReport).where(ExtensionReport.pdq_hash == body.pdq)
        )
        existing = result.scalars().first()
    if existing is None and body.sha256:
        result = await db.execute(
            select(ExtensionReport).where(ExtensionReport.sha256_hash == body.sha256)
        )
        existing = result.scalars().first()
    if existing is None and body.phash:
        result = await db.execute(
            select(ExtensionReport).where(ExtensionReport.phash == body.phash)
        )
        existing = result.scalars().first()

    if existing is not None:
        existing.observed_count += 1
        # Merge in any fields we did not have before (opportunistic).
        if not existing.sha256_hash and body.sha256:
            existing.sha256_hash = body.sha256
        if not existing.pdq_hash and body.pdq:
            existing.pdq_hash = body.pdq
        if not existing.phash and body.phash:
            existing.phash = body.phash
        if not existing.detected_promoter_text and body.detected_promoter_text:
            existing.detected_promoter_text = body.detected_promoter_text
        if not existing.page_url_host and body.page_url_host:
            existing.page_url_host = body.page_url_host
        await db.commit()
        return ExtensionReportResponse(
            accepted=True,
            report_id=existing.id,
            observed_count=existing.observed_count,
            deduplicated=True,
        )

    new_report = ExtensionReport(
        sha256_hash=body.sha256,
        pdq_hash=body.pdq,
        phash=body.phash,
        detected_promoter_text=body.detected_promoter_text,
        page_url_host=body.page_url_host,
    )
    db.add(new_report)
    await db.commit()
    await db.refresh(new_report)
    return ExtensionReportResponse(
        accepted=True,
        report_id=new_report.id,
        observed_count=1,
        deduplicated=False,
    )


@router.post("/flag", response_model=ExtensionFlagResponse)
async def submit_flag(
    request: Request,
    body: ExtensionFlagRequest,
    db: AsyncSession = Depends(get_db),
):
    """Accept a user-initiated flag from the extension.

    Flags are administrative triage input only. They are not published
    and do not trigger any automatic action. The Commission decides how
    to act on them.
    """
    ip_hash = _hash_ip(request)
    if not _rate_limit(
        f"flag:{ip_hash}", settings.RATE_LIMIT_EXTENSION_FLAG_PER_MINUTE
    ):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded",
        )

    flag = ExtensionFlag(
        sha256_hash=body.sha256,
        pdq_hash=body.pdq,
        phash=body.phash,
        reason=body.reason,
        note=body.note,
        page_url_host=body.page_url_host,
        source_ip_hash=ip_hash,
        status=FlagStatus.OPEN,
    )
    db.add(flag)
    await db.commit()
    await db.refresh(flag)
    return ExtensionFlagResponse(accepted=True, flag_id=flag.id)


# --------------------------------------------------------------------------
# Bloom-filter snapshot
# --------------------------------------------------------------------------

# Sized for the volumes estimated in the briefing (up to ~5,000 active
# assets) at a 0.1% false-positive rate. The resulting filter is around
# 9 KB, which is easy to download and refresh.
SNAPSHOT_TARGET_FPR = 0.001
SNAPSHOT_MIN_CAPACITY = 1024


@router.get("/bloom-snapshot")
async def bloom_snapshot(db: AsyncSession = Depends(get_db)):
    """Return a bloom filter containing every active asset's hashes.

    The extension downloads this once (and refreshes periodically),
    then queries it locally so the server never sees which images
    a user is browsing. A positive bloom hit may still be a false
    positive, in which case the extension confirms via /verify/hash.

    Response is binary (application/octet-stream) using the same
    versioned wire format that ``extension/src/lib/bloom`` parses.
    """
    result = await db.execute(
        select(Asset).where(Asset.status == AssetStatus.ACTIVE)
    )
    assets = result.scalars().all()

    capacity = max(SNAPSHOT_MIN_CAPACITY, len(assets) * 2)
    bf = BloomFilter.for_items(capacity, SNAPSHOT_TARGET_FPR)
    for a in assets:
        if a.sha256_hash:
            bf.add(a.sha256_hash)
        if a.pdq_hash:
            bf.add(a.pdq_hash)
        if a.phash:
            bf.add(a.phash)
    blob = bf.serialize()

    return Response(
        content=blob,
        media_type="application/octet-stream",
        headers={
            "X-PIVS-Bloom-Items": str(bf.item_count),
            "X-PIVS-Bloom-Bits": str(bf.num_bits),
            "X-PIVS-Bloom-Hashes": str(bf.num_hashes),
            "X-PIVS-Bloom-Generated-At": str(bf.generated_at_millis),
            "Cache-Control": "public, max-age=300",
        },
    )
