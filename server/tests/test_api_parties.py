"""Integration tests for the party management API."""

import pytest
from httpx import AsyncClient


class TestPublicPartyList:
    @pytest.mark.asyncio
    async def test_list_parties_public(
        self, client: AsyncClient, sample_party
    ):
        resp = await client.get("/api/v1/parties")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) >= 1
        assert data[0]["name"] == "Test Labour Party"
        # Should NOT include contact email (privacy)
        assert "contact_email" not in data[0]


class TestPartyCreation:
    @pytest.mark.asyncio
    async def test_create_party_requires_auth(self, client: AsyncClient):
        resp = await client.post(
            "/api/v1/parties",
            json={"name": "New Party", "short_name": "NP"},
        )
        assert resp.status_code == 401

    @pytest.mark.asyncio
    async def test_create_party_as_admin(
        self, client: AsyncClient, auth_headers: dict
    ):
        resp = await client.post(
            "/api/v1/parties",
            json={
                "name": "Another Party",
                "short_name": "AP",
                "registration_number": "REG999",
            },
            headers=auth_headers,
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["name"] == "Another Party"
        assert data["short_name"] == "AP"
        assert data["status"] == "active"

    @pytest.mark.asyncio
    async def test_create_duplicate_party_fails(
        self, client: AsyncClient, auth_headers: dict, sample_party
    ):
        resp = await client.post(
            "/api/v1/parties",
            json={"name": "Test Labour Party", "short_name": "Labour2"},
            headers=auth_headers,
        )
        assert resp.status_code == 409


class TestHealthAndRoot:
    @pytest.mark.asyncio
    async def test_health(self, client: AsyncClient):
        resp = await client.get("/health")
        assert resp.status_code == 200
        assert resp.json()["status"] == "ok"

    @pytest.mark.asyncio
    async def test_root(self, client: AsyncClient):
        resp = await client.get("/")
        assert resp.status_code == 200
        data = resp.json()
        assert "NZ Political Image Verification" in data["name"]
