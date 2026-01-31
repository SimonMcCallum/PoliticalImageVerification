"""Integration tests for the auth API endpoints."""

import pytest
from httpx import AsyncClient

from app.models.party import PartyUser


class TestLogin:
    @pytest.mark.asyncio
    async def test_login_success(self, client: AsyncClient, admin_user: PartyUser):
        resp = await client.post(
            "/api/v1/auth/login",
            json={"username": "testadmin", "password": "testpass123"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    @pytest.mark.asyncio
    async def test_login_wrong_password(self, client: AsyncClient, admin_user: PartyUser):
        resp = await client.post(
            "/api/v1/auth/login",
            json={"username": "testadmin", "password": "wrongpass"},
        )
        assert resp.status_code == 401

    @pytest.mark.asyncio
    async def test_login_nonexistent_user(self, client: AsyncClient):
        resp = await client.post(
            "/api/v1/auth/login",
            json={"username": "nobody", "password": "pass"},
        )
        assert resp.status_code == 401

    @pytest.mark.asyncio
    async def test_login_returns_usable_token(
        self, client: AsyncClient, admin_user: PartyUser
    ):
        resp = await client.post(
            "/api/v1/auth/login",
            json={"username": "testadmin", "password": "testpass123"},
        )
        token = resp.json()["access_token"]
        # Use the token to hit an authenticated endpoint
        resp2 = await client.get(
            "/api/v1/assets",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp2.status_code == 200
