"""Integration tests for the extension report/flag endpoints and the
Electoral Commission review queue.
"""

import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import create_access_token, hash_password
from app.models.extension import (
    ExtensionFlag,
    ExtensionReport,
    FlagReason,
    FlagStatus,
    ReportStatus,
)
from app.models.party import Party, PartyStatus, PartyUser, UserRole
from app.services.encryption import encrypt_string


# --------------------------------------------------------------------------
# Fixtures for an Electoral Commission user (separate from the party admin
# fixtures already in conftest.py).
# --------------------------------------------------------------------------


@pytest_asyncio.fixture
async def ec_party(db_session: AsyncSession) -> Party:
    party = Party(
        name="Electoral Commission",
        short_name="EC",
        registration_number="EC-AUTH",
        status=PartyStatus.ACTIVE,
        contact_email_encrypted=encrypt_string("ec@example.nz"),
    )
    db_session.add(party)
    await db_session.commit()
    await db_session.refresh(party)
    return party


@pytest_asyncio.fixture
async def ec_user(db_session: AsyncSession, ec_party: Party) -> PartyUser:
    user = PartyUser(
        party_id=ec_party.id,
        username="ecuser",
        email_encrypted=encrypt_string("ec@example.nz"),
        hashed_password=hash_password("ecpass123"),
        role=UserRole.ELECTORAL_COMMISSION,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def ec_headers(ec_user: PartyUser) -> dict:
    token = create_access_token(ec_user.id, ec_user.party_id, ec_user.role.value)
    return {"Authorization": f"Bearer {token}"}


# --------------------------------------------------------------------------
# /api/v1/extension/report
# --------------------------------------------------------------------------


class TestExtensionReport:
    @pytest.mark.asyncio
    async def test_report_new_image_accepted(self, client: AsyncClient):
        resp = await client.post(
            "/api/v1/extension/report",
            json={
                "sha256": "a" * 64,
                "pdq": "b" * 64,
                "phash": "c" * 16,
                "detected_promoter_text": "Authorised by J. Smith, 1 Test St",
                "page_url_host": "example.com",
            },
        )
        assert resp.status_code == 200, resp.text
        data = resp.json()
        assert data["accepted"] is True
        assert data["observed_count"] == 1
        assert data["deduplicated"] is False
        assert data["report_id"] is not None

    @pytest.mark.asyncio
    async def test_report_requires_at_least_one_hash(self, client: AsyncClient):
        resp = await client.post(
            "/api/v1/extension/report",
            json={"page_url_host": "example.com"},
        )
        assert resp.status_code == 400

    @pytest.mark.asyncio
    async def test_report_dedups_on_pdq(self, client: AsyncClient):
        payload = {
            "pdq": "d" * 64,
            "detected_promoter_text": "Authorised by K. Jones",
            "page_url_host": "facebook.com",
        }
        first = await client.post("/api/v1/extension/report", json=payload)
        second = await client.post("/api/v1/extension/report", json=payload)
        third = await client.post("/api/v1/extension/report", json=payload)
        assert first.status_code == 200
        assert second.status_code == 200
        assert third.status_code == 200
        assert first.json()["deduplicated"] is False
        assert second.json()["deduplicated"] is True
        assert third.json()["deduplicated"] is True
        assert third.json()["observed_count"] == 3
        # All three share the same report_id
        assert first.json()["report_id"] == second.json()["report_id"]
        assert first.json()["report_id"] == third.json()["report_id"]

    @pytest.mark.asyncio
    async def test_report_dedups_on_sha256_when_no_pdq(self, client: AsyncClient):
        payload = {
            "sha256": "e" * 64,
            "detected_promoter_text": "Authorised by L. Brown",
        }
        first = await client.post("/api/v1/extension/report", json=payload)
        second = await client.post("/api/v1/extension/report", json=payload)
        assert first.json()["report_id"] == second.json()["report_id"]
        assert second.json()["observed_count"] == 2

    @pytest.mark.asyncio
    async def test_report_persists_to_db(
        self, client: AsyncClient, db_session: AsyncSession
    ):
        await client.post(
            "/api/v1/extension/report",
            json={"pdq": "f" * 64, "page_url_host": "twitter.com"},
        )
        from sqlalchemy import select

        result = await db_session.execute(select(ExtensionReport))
        rows = result.scalars().all()
        assert len(rows) == 1
        assert rows[0].pdq_hash == "f" * 64
        assert rows[0].status == ReportStatus.OPEN
        assert rows[0].observed_count == 1


# --------------------------------------------------------------------------
# /api/v1/extension/flag
# --------------------------------------------------------------------------


class TestExtensionFlag:
    @pytest.mark.asyncio
    async def test_flag_accepted(self, client: AsyncClient):
        resp = await client.post(
            "/api/v1/extension/flag",
            json={
                "sha256": "1" * 64,
                "reason": "misattributed",
                "note": "Looks like a fake campaign image",
                "page_url_host": "example.com",
            },
        )
        assert resp.status_code == 200, resp.text
        data = resp.json()
        assert data["accepted"] is True
        assert data["flag_id"] is not None

    @pytest.mark.asyncio
    async def test_flag_invalid_reason(self, client: AsyncClient):
        resp = await client.post(
            "/api/v1/extension/flag",
            json={"sha256": "1" * 64, "reason": "not_a_real_reason"},
        )
        assert resp.status_code == 422

    @pytest.mark.asyncio
    async def test_flag_persists_to_db(
        self, client: AsyncClient, db_session: AsyncSession
    ):
        await client.post(
            "/api/v1/extension/flag",
            json={
                "pdq": "2" * 64,
                "reason": "promoter_statement_fake",
                "note": "The promoter address does not look real",
            },
        )
        from sqlalchemy import select

        result = await db_session.execute(select(ExtensionFlag))
        rows = result.scalars().all()
        assert len(rows) == 1
        assert rows[0].reason == FlagReason.PROMOTER_STATEMENT_FAKE
        assert rows[0].status == FlagStatus.OPEN
        assert rows[0].source_ip_hash is not None  # IP hash recorded


# --------------------------------------------------------------------------
# /api/v1/ec/review-queue/*
# --------------------------------------------------------------------------


class TestReviewQueue:
    @pytest.mark.asyncio
    async def test_reports_requires_ec_role(
        self, client: AsyncClient, auth_headers: dict
    ):
        """A regular party admin must not be able to list the queue."""
        resp = await client.get(
            "/api/v1/ec/review-queue/reports", headers=auth_headers
        )
        assert resp.status_code == 403

    @pytest.mark.asyncio
    async def test_reports_unauthenticated_forbidden(self, client: AsyncClient):
        resp = await client.get("/api/v1/ec/review-queue/reports")
        assert resp.status_code == 401

    @pytest.mark.asyncio
    async def test_ec_can_list_reports(
        self, client: AsyncClient, ec_headers: dict
    ):
        # Create a couple of reports
        await client.post(
            "/api/v1/extension/report",
            json={"pdq": "a" * 64, "page_url_host": "foo.com"},
        )
        await client.post(
            "/api/v1/extension/report",
            json={"pdq": "b" * 64, "page_url_host": "bar.com"},
        )
        resp = await client.get(
            "/api/v1/ec/review-queue/reports", headers=ec_headers
        )
        assert resp.status_code == 200, resp.text
        data = resp.json()
        assert len(data) == 2
        hashes = {entry["pdq"] for entry in data}
        assert hashes == {"a" * 64, "b" * 64}

    @pytest.mark.asyncio
    async def test_list_reports_ordered_by_observed_count_desc(
        self, client: AsyncClient, ec_headers: dict
    ):
        # Same hash twice -> observed_count = 2
        await client.post("/api/v1/extension/report", json={"pdq": "a" * 64})
        await client.post("/api/v1/extension/report", json={"pdq": "a" * 64})
        # Different hash, observed once
        await client.post("/api/v1/extension/report", json={"pdq": "b" * 64})

        resp = await client.get(
            "/api/v1/ec/review-queue/reports", headers=ec_headers
        )
        data = resp.json()
        assert data[0]["observed_count"] == 2
        assert data[0]["pdq"] == "a" * 64
        assert data[1]["observed_count"] == 1

    @pytest.mark.asyncio
    async def test_dismiss_report(
        self, client: AsyncClient, ec_headers: dict
    ):
        create = await client.post(
            "/api/v1/extension/report", json={"pdq": "c" * 64}
        )
        report_id = create.json()["report_id"]

        resp = await client.post(
            f"/api/v1/ec/review-queue/reports/{report_id}/dismiss",
            headers=ec_headers,
        )
        assert resp.status_code == 200

        listing = await client.get(
            "/api/v1/ec/review-queue/reports?status=open", headers=ec_headers
        )
        assert listing.json() == []

        dismissed = await client.get(
            "/api/v1/ec/review-queue/reports?status=dismissed",
            headers=ec_headers,
        )
        assert len(dismissed.json()) == 1

    @pytest.mark.asyncio
    async def test_triage_report(
        self, client: AsyncClient, ec_headers: dict
    ):
        create = await client.post(
            "/api/v1/extension/report", json={"pdq": "d" * 64}
        )
        report_id = create.json()["report_id"]

        resp = await client.post(
            f"/api/v1/ec/review-queue/reports/{report_id}/triage",
            headers=ec_headers,
        )
        assert resp.status_code == 200

        triaged = await client.get(
            "/api/v1/ec/review-queue/reports?status=triaged",
            headers=ec_headers,
        )
        assert len(triaged.json()) == 1

    @pytest.mark.asyncio
    async def test_list_flags(
        self, client: AsyncClient, ec_headers: dict
    ):
        await client.post(
            "/api/v1/extension/flag",
            json={"sha256": "1" * 64, "reason": "content_concern"},
        )
        resp = await client.get(
            "/api/v1/ec/review-queue/flags", headers=ec_headers
        )
        assert resp.status_code == 200
        assert len(resp.json()) == 1
        assert resp.json()[0]["reason"] == "content_concern"

    @pytest.mark.asyncio
    async def test_summary_counts(
        self, client: AsyncClient, ec_headers: dict
    ):
        await client.post("/api/v1/extension/report", json={"pdq": "e" * 64})
        await client.post(
            "/api/v1/extension/flag",
            json={"sha256": "2" * 64, "reason": "misattributed"},
        )

        resp = await client.get(
            "/api/v1/ec/review-queue/summary", headers=ec_headers
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["reports"]["open"] == 1
        assert data["flags"]["open"] == 1

    @pytest.mark.asyncio
    async def test_dismiss_flag(
        self, client: AsyncClient, ec_headers: dict
    ):
        create = await client.post(
            "/api/v1/extension/flag",
            json={"sha256": "3" * 64, "reason": "other"},
        )
        flag_id = create.json()["flag_id"]
        resp = await client.post(
            f"/api/v1/ec/review-queue/flags/{flag_id}/dismiss",
            headers=ec_headers,
        )
        assert resp.status_code == 200


# --------------------------------------------------------------------------
# /api/v1/extension/bloom-snapshot
# --------------------------------------------------------------------------


class TestBloomSnapshot:
    @pytest.mark.asyncio
    async def test_snapshot_is_publicly_accessible(self, client: AsyncClient):
        """No auth required (extension is anonymous)."""
        resp = await client.get("/api/v1/extension/bloom-snapshot")
        assert resp.status_code == 200
        assert resp.headers["content-type"] == "application/octet-stream"
        assert int(resp.headers["x-pivs-bloom-bits"]) > 0
        assert int(resp.headers["x-pivs-bloom-hashes"]) > 0

    @pytest.mark.asyncio
    async def test_snapshot_has_correct_magic(self, client: AsyncClient):
        resp = await client.get("/api/v1/extension/bloom-snapshot")
        body = resp.content
        assert body[:4] == b"PIBF"
        assert body[4] == 1  # version

    @pytest.mark.asyncio
    async def test_snapshot_includes_active_assets(
        self, client: AsyncClient, db_session: AsyncSession, sample_party, admin_user
    ):
        """Active asset hashes should appear as bloom hits."""
        from app.models.asset import Asset, AssetStatus
        from app.services.bloom import BloomFilter
        from app.services.encryption import encrypt_string

        known_sha = "a" * 64
        known_pdq = "b" * 64
        known_phash = "c" * 16
        asset = Asset(
            party_id=sample_party.id,
            submitted_by=admin_user.id,
            original_filename_encrypted=encrypt_string("known.png"),
            mime_type="image/png",
            file_size=1024,
            sha256_hash=known_sha,
            pdq_hash=known_pdq,
            pdq_quality=100,
            phash=known_phash,
            encrypted_storage_key="x|y",
            encryption_iv="0" * 24,
            verification_id="known001",
            status=AssetStatus.ACTIVE,
        )
        db_session.add(asset)
        await db_session.commit()

        resp = await client.get("/api/v1/extension/bloom-snapshot")
        assert resp.status_code == 200

        # Parse the snapshot using the matching Python class.
        from app.services.bloom import HEADER_BYTES
        import struct

        body = resp.content
        num_bits = struct.unpack_from("<I", body, 6)[0]
        num_hashes = struct.unpack_from("<H", body, 10)[0]
        bits = bytearray(body[HEADER_BYTES:])
        bf = BloomFilter(num_bits=num_bits, num_hashes=num_hashes, bits=bits)

        assert bf.might_contain(known_sha)
        assert bf.might_contain(known_pdq)
        assert bf.might_contain(known_phash)
        # An obviously absent hash should not match.
        assert not bf.might_contain("z" * 64)
