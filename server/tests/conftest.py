"""
Shared test fixtures.

Uses SQLite (aiosqlite) for tests so no PostgreSQL is needed.
Overrides the database dependency for the FastAPI app.
"""

import io
import os
import shutil
import uuid

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from PIL import Image
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

# Set test env vars BEFORE importing app code
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///./test.db"
os.environ["STORAGE_BACKEND"] = "local"
os.environ["LOCAL_STORAGE_PATH"] = "./test_storage"
os.environ["MASTER_ENCRYPTION_KEY"] = (
    "0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef"
)
os.environ["SECRET_KEY"] = "test-secret-key-not-for-production"

from app.core.auth import create_access_token, hash_password
from app.core.database import Base, get_db
from app.main import app
from app.models.party import Party, PartyUser, PartyStatus, UserRole
from app.services.encryption import encrypt_string

TEST_DB_URL = "sqlite+aiosqlite:///./test.db"

engine = create_async_engine(TEST_DB_URL, echo=False)
TestSession = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def override_get_db():
    async with TestSession() as session:
        try:
            yield session
        finally:
            await session.close()


app.dependency_overrides[get_db] = override_get_db


@pytest_asyncio.fixture(autouse=True)
async def setup_db():
    """Create tables before each test, drop after."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    # Clean up test storage
    if os.path.exists("./test_storage"):
        shutil.rmtree("./test_storage")
    if os.path.exists("./test.db"):
        os.remove("./test.db")


@pytest_asyncio.fixture
async def db_session():
    async with TestSession() as session:
        yield session


@pytest_asyncio.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c


@pytest_asyncio.fixture
async def sample_party(db_session: AsyncSession) -> Party:
    """Create a sample party in the DB."""
    party = Party(
        name="Test Labour Party",
        short_name="Labour",
        registration_number="REG001",
        status=PartyStatus.ACTIVE,
        contact_email_encrypted=encrypt_string("test@labour.org.nz"),
    )
    db_session.add(party)
    await db_session.commit()
    await db_session.refresh(party)
    return party


@pytest_asyncio.fixture
async def admin_user(db_session: AsyncSession, sample_party: Party) -> PartyUser:
    """Create an admin user for the sample party."""
    user = PartyUser(
        party_id=sample_party.id,
        username="testadmin",
        email_encrypted=encrypt_string("admin@test.com"),
        hashed_password=hash_password("testpass123"),
        role=UserRole.ADMIN,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def admin_token(admin_user: PartyUser) -> str:
    """Create a JWT token for the admin user."""
    return create_access_token(admin_user.id, admin_user.party_id, admin_user.role.value)


@pytest_asyncio.fixture
async def auth_headers(admin_token: str) -> dict:
    """Authorization headers for authenticated requests."""
    return {"Authorization": f"Bearer {admin_token}"}


def create_test_image(width: int = 200, height: int = 200, color: str = "red") -> bytes:
    """Create a simple test image and return its bytes."""
    img = Image.new("RGB", (width, height), color)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()
