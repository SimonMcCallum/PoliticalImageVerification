"""Asset submission endpoints for authenticated party users."""

import json
import secrets
import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from fastapi.responses import Response
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_current_user, require_submitter
from app.core.config import settings
from app.core.database import get_db
from app.models.asset import Asset, AssetStatus
from app.models.party import Party, PartyUser
from app.schemas.asset import AssetListItem, AssetMetadataUpdate, AssetResponse
from app.services.badge import generate_badge_overlay, generate_qr_code
from app.services.encryption import encrypt_data, generate_dek, encrypt_dek, encrypt_string
from app.services.hashing import compute_all_hashes
from app.services.promoter_overlay import overlay_promoter_statement, VALID_POSITIONS
from app.services.storage import store_blob

router = APIRouter(prefix="/assets", tags=["assets"])

ALLOWED_MIME_TYPES = {
    "image/jpeg",
    "image/png",
    "image/webp",
    "image/svg+xml",
    "application/pdf",
}
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB


def _generate_verification_id() -> str:
    """Generate a short, URL-safe verification ID."""
    return secrets.token_urlsafe(8)[:10]


@router.post("", response_model=AssetResponse, status_code=status.HTTP_201_CREATED)
async def submit_asset(
    file: UploadFile = File(...),
    metadata: str | None = Form(None),
    badge_position: str | None = Form(None),
    add_promoter_statement: bool = Form(False),
    promoter_position: str | None = Form(None),
    check_promoter_statement: bool = Form(False),
    user: PartyUser = Depends(require_submitter),
    db: AsyncSession = Depends(get_db),
):
    """Submit an image asset for verification registration.

    Optional promoter statement features:
    - add_promoter_statement: overlay the party's promoter statement on the image
    - promoter_position: corner for promoter text (top-left, top-right, bottom-left, bottom-right)
    - check_promoter_statement: OCR the image to check for existing promoter statement
    """
    # Validate file type
    if file.content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file type: {file.content_type}. Allowed: {ALLOWED_MIME_TYPES}",
        )

    # Read file bytes
    image_bytes = await file.read()
    if len(image_bytes) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File too large. Maximum size is {MAX_FILE_SIZE // (1024*1024)}MB",
        )
    if len(image_bytes) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Empty file",
        )

    # Get party info
    party_result = await db.execute(select(Party).where(Party.id == user.party_id))
    party = party_result.scalar_one()

    # OCR check for promoter statement if requested
    promoter_check_result = None
    if check_promoter_statement:
        if not party.promoter_statement:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No promoter statement set for this party. Set one first via the party settings.",
            )
        from app.services.ocr import find_promoter_statement
        promoter_check_result = find_promoter_statement(image_bytes, party.promoter_statement)

    # Add promoter statement overlay if requested
    promoter_storage_key = None
    if add_promoter_statement:
        if not party.promoter_statement:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No promoter statement set for this party. Set one first via the party settings.",
            )
        position = promoter_position or user.default_statement_position
        if position not in VALID_POSITIONS:
            position = "bottom-left"

        promoter_bytes = overlay_promoter_statement(
            image_bytes, party.promoter_statement, position=position
        )
        # Encrypt and store the promoter-stamped version
        promoter_dek = generate_dek()
        encrypted_promoter, promoter_nonce = encrypt_data(promoter_bytes, promoter_dek)
        encrypted_promoter_dek = encrypt_dek(promoter_dek)
        promoter_storage_key = await store_blob(encrypted_promoter, prefix="promoter")

    # Compute hashes on the original image (before any badge overlay)
    hashes = compute_all_hashes(image_bytes)

    # Generate verification ID
    verification_id = _generate_verification_id()

    # Encrypt and store original image
    dek = generate_dek()
    encrypted_image, nonce = encrypt_data(image_bytes, dek)
    encrypted_dek = encrypt_dek(dek)
    storage_key = await store_blob(encrypted_image, prefix="assets")

    # Generate and store QR code
    qr_bytes = generate_qr_code(verification_id)
    qr_storage_key = await store_blob(qr_bytes, prefix="qrcodes")

    # Generate and store badge overlay image
    badge_bytes = generate_badge_overlay(
        image_bytes, verification_id, party.short_name, badge_position
    )
    badge_dek = generate_dek()
    encrypted_badge, badge_nonce = encrypt_data(badge_bytes, badge_dek)
    badge_storage_key = await store_blob(encrypted_badge, prefix="badges")

    # Parse metadata JSON
    metadata_dict = None
    if metadata:
        try:
            metadata_dict = json.loads(metadata)
        except json.JSONDecodeError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid JSON in metadata field",
            )

    # Create asset record
    asset = Asset(
        party_id=user.party_id,
        submitted_by=user.id,
        original_filename_encrypted=encrypt_string(file.filename or "unknown"),
        mime_type=file.content_type,
        file_size=len(image_bytes),
        sha256_hash=hashes["sha256"],
        pdq_hash=hashes["pdq_hash"],
        pdq_quality=hashes["pdq_quality"],
        phash=hashes["phash"],
        encrypted_storage_key=f"{storage_key}|{encrypted_dek}",
        encryption_iv=nonce.hex(),
        badge_storage_key=badge_storage_key,
        promoter_storage_key=promoter_storage_key,
        qr_code_storage_key=qr_storage_key,
        verification_id=verification_id,
        metadata_json=metadata_dict,
    )
    db.add(asset)
    await db.commit()
    await db.refresh(asset)

    verification_url = f"{settings.VERIFICATION_BASE_URL}/{verification_id}"
    return AssetResponse(
        id=asset.id,
        party_id=asset.party_id,
        mime_type=asset.mime_type,
        file_size=asset.file_size,
        sha256_hash=asset.sha256_hash,
        pdq_hash=asset.pdq_hash,
        pdq_quality=asset.pdq_quality,
        phash=asset.phash,
        verification_id=asset.verification_id,
        verification_url=verification_url,
        badge_url=f"{settings.API_V1_PREFIX}/assets/{asset.id}/badge",
        qr_code_url=f"{settings.API_V1_PREFIX}/assets/{asset.id}/qrcode",
        promoter_image_url=(
            f"{settings.API_V1_PREFIX}/assets/{asset.id}/promoter"
            if promoter_storage_key else None
        ),
        metadata=asset.metadata_json,
        promoter_check=promoter_check_result,
        status=asset.status,
        created_at=asset.created_at,
        expires_at=asset.expires_at,
    )


@router.post("/add-promoter")
async def add_promoter_to_image(
    file: UploadFile = File(...),
    position: str | None = Form(None),
    user: PartyUser = Depends(require_submitter),
    db: AsyncSession = Depends(get_db),
):
    """Batch mode: add promoter statement to an image and return it directly.

    Does NOT register the image as an asset. Returns the modified image
    as PNG bytes for download.
    """
    if file.content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file type: {file.content_type}",
        )

    image_bytes = await file.read()
    if len(image_bytes) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File too large. Maximum size is {MAX_FILE_SIZE // (1024*1024)}MB",
        )
    if len(image_bytes) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Empty file",
        )

    # Get party's promoter statement
    party_result = await db.execute(select(Party).where(Party.id == user.party_id))
    party = party_result.scalar_one()

    if not party.promoter_statement:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No promoter statement set for this party. Set one first via the party settings.",
        )

    pos = position or user.default_statement_position
    if pos not in VALID_POSITIONS:
        pos = "bottom-left"

    result_bytes = overlay_promoter_statement(
        image_bytes, party.promoter_statement, position=pos
    )
    return Response(
        content=result_bytes,
        media_type="image/png",
        headers={"Content-Disposition": "attachment; filename=promoter_stamped.png"},
    )


@router.get("", response_model=list[AssetListItem])
async def list_assets(
    page: int = 1,
    per_page: int = 50,
    user: PartyUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List assets for the current user's party."""
    offset = (page - 1) * per_page
    result = await db.execute(
        select(Asset)
        .where(Asset.party_id == user.party_id)
        .order_by(Asset.created_at.desc())
        .offset(offset)
        .limit(per_page)
    )
    assets = result.scalars().all()
    return assets


@router.get("/{asset_id}", response_model=AssetResponse)
async def get_asset(
    asset_id: uuid.UUID,
    user: PartyUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Asset).where(Asset.id == asset_id, Asset.party_id == user.party_id)
    )
    asset = result.scalar_one_or_none()
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")

    verification_url = f"{settings.VERIFICATION_BASE_URL}/{asset.verification_id}"
    return AssetResponse(
        id=asset.id,
        party_id=asset.party_id,
        mime_type=asset.mime_type,
        file_size=asset.file_size,
        sha256_hash=asset.sha256_hash,
        pdq_hash=asset.pdq_hash,
        pdq_quality=asset.pdq_quality,
        phash=asset.phash,
        verification_id=asset.verification_id,
        verification_url=verification_url,
        badge_url=f"{settings.API_V1_PREFIX}/assets/{asset.id}/badge",
        qr_code_url=f"{settings.API_V1_PREFIX}/assets/{asset.id}/qrcode",
        promoter_image_url=(
            f"{settings.API_V1_PREFIX}/assets/{asset.id}/promoter"
            if asset.promoter_storage_key else None
        ),
        metadata=asset.metadata_json,
        status=asset.status,
        created_at=asset.created_at,
        expires_at=asset.expires_at,
    )


@router.patch("/{asset_id}", response_model=AssetResponse)
async def update_asset(
    asset_id: uuid.UUID,
    body: AssetMetadataUpdate,
    user: PartyUser = Depends(require_submitter),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Asset).where(Asset.id == asset_id, Asset.party_id == user.party_id)
    )
    asset = result.scalar_one_or_none()
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")

    if body.metadata is not None:
        asset.metadata_json = body.metadata
    if body.status == AssetStatus.REVOKED:
        asset.status = AssetStatus.REVOKED
        asset.revoked_at = datetime.now(timezone.utc)

    await db.commit()
    await db.refresh(asset)

    verification_url = f"{settings.VERIFICATION_BASE_URL}/{asset.verification_id}"
    return AssetResponse(
        id=asset.id,
        party_id=asset.party_id,
        mime_type=asset.mime_type,
        file_size=asset.file_size,
        sha256_hash=asset.sha256_hash,
        pdq_hash=asset.pdq_hash,
        pdq_quality=asset.pdq_quality,
        phash=asset.phash,
        verification_id=asset.verification_id,
        verification_url=verification_url,
        badge_url=f"{settings.API_V1_PREFIX}/assets/{asset.id}/badge",
        qr_code_url=f"{settings.API_V1_PREFIX}/assets/{asset.id}/qrcode",
        promoter_image_url=(
            f"{settings.API_V1_PREFIX}/assets/{asset.id}/promoter"
            if asset.promoter_storage_key else None
        ),
        metadata=asset.metadata_json,
        status=asset.status,
        created_at=asset.created_at,
        expires_at=asset.expires_at,
    )


@router.get("/{asset_id}/qrcode")
async def get_asset_qr_code(
    asset_id: uuid.UUID,
    user: PartyUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Download the QR code PNG for an asset."""
    from app.services.storage import retrieve_blob

    result = await db.execute(
        select(Asset).where(Asset.id == asset_id, Asset.party_id == user.party_id)
    )
    asset = result.scalar_one_or_none()
    if not asset or not asset.qr_code_storage_key:
        raise HTTPException(status_code=404, detail="Asset or QR code not found")

    qr_bytes = await retrieve_blob(asset.qr_code_storage_key)
    return Response(content=qr_bytes, media_type="image/png")


@router.get("/{asset_id}/promoter")
async def get_asset_promoter_image(
    asset_id: uuid.UUID,
    user: PartyUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Download the promoter-stamped version of an asset."""
    from app.services.storage import retrieve_blob

    result = await db.execute(
        select(Asset).where(Asset.id == asset_id, Asset.party_id == user.party_id)
    )
    asset = result.scalar_one_or_none()
    if not asset or not asset.promoter_storage_key:
        raise HTTPException(status_code=404, detail="Asset or promoter image not found")

    promoter_bytes = await retrieve_blob(asset.promoter_storage_key)
    return Response(content=promoter_bytes, media_type="image/png")
