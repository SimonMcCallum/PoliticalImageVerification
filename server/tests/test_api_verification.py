"""Integration tests for the public verification API."""

import io
import uuid

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.asset import Asset, AssetStatus
from app.models.party import Party
from app.services.encryption import encrypt_string
from app.services.hashing import compute_all_hashes
from tests.conftest import create_test_image


async def _insert_test_asset(
    db: AsyncSession, party: Party, user_id: uuid.UUID, image_bytes: bytes
) -> Asset:
    """Insert a test asset directly into the database."""
    hashes = compute_all_hashes(image_bytes)
    asset = Asset(
        party_id=party.id,
        submitted_by=user_id,
        original_filename_encrypted=encrypt_string("test.png"),
        mime_type="image/png",
        file_size=len(image_bytes),
        sha256_hash=hashes["sha256"],
        pdq_hash=hashes["pdq_hash"],
        pdq_quality=hashes["pdq_quality"],
        phash=hashes["phash"],
        encrypted_storage_key="test/fake_key|fake_dek",
        encryption_iv="0" * 24,
        verification_id="testver123",
        status=AssetStatus.ACTIVE,
    )
    db.add(asset)
    await db.commit()
    await db.refresh(asset)
    return asset


class TestVerifyImage:
    @pytest.mark.asyncio
    async def test_verify_unregistered_image(self, client: AsyncClient):
        img = create_test_image(color="purple")
        resp = await client.post(
            "/api/v1/verify/image",
            files={"file": ("test.png", img, "image/png")},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["verified"] is False
        assert data["result"] == "unverified"

    @pytest.mark.asyncio
    async def test_verify_registered_image_exact_match(
        self, client: AsyncClient, db_session: AsyncSession, sample_party, admin_user
    ):
        img = create_test_image(color="red")
        await _insert_test_asset(db_session, sample_party, admin_user.id, img)

        resp = await client.post(
            "/api/v1/verify/image",
            files={"file": ("test.png", img, "image/png")},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["verified"] is True
        assert data["match_type"] == "exact"
        assert data["confidence"] == 1.0
        assert data["party"]["short_name"] == "Labour"

    @pytest.mark.asyncio
    async def test_verify_resized_image_perceptual_match(
        self, client: AsyncClient, db_session: AsyncSession, sample_party, admin_user
    ):
        """A resized version should still match via PDQ perceptual hash."""
        from PIL import Image as PILImage

        original = create_test_image(width=400, height=400, color="green")
        await _insert_test_asset(db_session, sample_party, admin_user.id, original)

        # Resize the image
        img = PILImage.open(io.BytesIO(original))
        img_resized = img.resize((200, 200), PILImage.LANCZOS)
        buf = io.BytesIO()
        img_resized.save(buf, format="PNG")
        resized_bytes = buf.getvalue()

        resp = await client.post(
            "/api/v1/verify/image",
            files={"file": ("resized.png", resized_bytes, "image/png")},
        )
        assert resp.status_code == 200
        data = resp.json()
        # Should match perceptually (solid color images resize well)
        assert data["verified"] is True
        assert data["match_type"] in ("exact", "perceptual")


class TestVerifyById:
    @pytest.mark.asyncio
    async def test_valid_verification_id(
        self, client: AsyncClient, db_session: AsyncSession, sample_party, admin_user
    ):
        img = create_test_image()
        asset = await _insert_test_asset(
            db_session, sample_party, admin_user.id, img
        )

        resp = await client.get(f"/api/v1/verify/{asset.verification_id}")
        assert resp.status_code == 200
        data = resp.json()
        assert data["verified"] is True
        assert data["party_name"] == "Test Labour Party"
        assert data["party_short_name"] == "Labour"

    @pytest.mark.asyncio
    async def test_invalid_verification_id(self, client: AsyncClient):
        resp = await client.get("/api/v1/verify/nonexistent")
        assert resp.status_code == 200
        data = resp.json()
        assert data["verified"] is False
        assert data["status"] == "not_found"


class TestVerifyHash:
    @pytest.mark.asyncio
    async def test_verify_by_sha256(
        self, client: AsyncClient, db_session: AsyncSession, sample_party, admin_user
    ):
        img = create_test_image(color="yellow")
        asset = await _insert_test_asset(
            db_session, sample_party, admin_user.id, img
        )

        hashes = compute_all_hashes(img)
        resp = await client.post(
            "/api/v1/verify/hash",
            json={"sha256": hashes["sha256"]},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["verified"] is True
        assert data["match_type"] == "exact"

    @pytest.mark.asyncio
    async def test_verify_no_hashes_returns_error(self, client: AsyncClient):
        resp = await client.post("/api/v1/verify/hash", json={})
        assert resp.status_code == 200
        data = resp.json()
        assert data["result"] == "error"
