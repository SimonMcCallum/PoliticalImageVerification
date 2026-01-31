"""Integration tests for the asset submission API."""

import pytest
from httpx import AsyncClient

from tests.conftest import create_test_image


class TestAssetSubmission:
    @pytest.mark.asyncio
    async def test_submit_image_requires_auth(self, client: AsyncClient):
        img = create_test_image()
        resp = await client.post(
            "/api/v1/assets",
            files={"file": ("test.png", img, "image/png")},
        )
        assert resp.status_code == 401

    @pytest.mark.asyncio
    async def test_submit_image_success(
        self, client: AsyncClient, auth_headers: dict, sample_party
    ):
        img = create_test_image(color="blue")
        resp = await client.post(
            "/api/v1/assets",
            files={"file": ("campaign.png", img, "image/png")},
            headers=auth_headers,
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["mime_type"] == "image/png"
        assert data["status"] == "active"
        assert len(data["sha256_hash"]) == 64
        assert len(data["pdq_hash"]) == 64
        assert data["verification_id"] is not None
        assert data["verification_url"] is not None

    @pytest.mark.asyncio
    async def test_submit_invalid_file_type(
        self, client: AsyncClient, auth_headers: dict
    ):
        resp = await client.post(
            "/api/v1/assets",
            files={"file": ("test.txt", b"not an image", "text/plain")},
            headers=auth_headers,
        )
        assert resp.status_code == 400

    @pytest.mark.asyncio
    async def test_submit_empty_file(
        self, client: AsyncClient, auth_headers: dict
    ):
        resp = await client.post(
            "/api/v1/assets",
            files={"file": ("empty.png", b"", "image/png")},
            headers=auth_headers,
        )
        assert resp.status_code == 400


class TestAssetListing:
    @pytest.mark.asyncio
    async def test_list_assets_empty(
        self, client: AsyncClient, auth_headers: dict
    ):
        resp = await client.get("/api/v1/assets", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json() == []

    @pytest.mark.asyncio
    async def test_list_assets_after_submit(
        self, client: AsyncClient, auth_headers: dict, sample_party
    ):
        img = create_test_image(color="red")
        await client.post(
            "/api/v1/assets",
            files={"file": ("img.png", img, "image/png")},
            headers=auth_headers,
        )

        resp = await client.get("/api/v1/assets", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 1
        assert data[0]["status"] == "active"


class TestAssetRevocation:
    @pytest.mark.asyncio
    async def test_revoke_asset(
        self, client: AsyncClient, auth_headers: dict, sample_party
    ):
        img = create_test_image()
        submit_resp = await client.post(
            "/api/v1/assets",
            files={"file": ("img.png", img, "image/png")},
            headers=auth_headers,
        )
        asset_id = submit_resp.json()["id"]

        resp = await client.patch(
            f"/api/v1/assets/{asset_id}",
            json={"status": "revoked"},
            headers=auth_headers,
        )
        assert resp.status_code == 200
        assert resp.json()["status"] == "revoked"
