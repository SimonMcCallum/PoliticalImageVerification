"""
NZ Political Image Verification System - API Server

FastAPI application that provides:
- Public verification API (no auth required)
- Party asset submission API (authenticated)
- Party management API (admin only)
"""

from contextlib import asynccontextmanager
import traceback

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

import asyncio
import logging

from app.core.config import settings
from app.core.database import init_db
from app.api import (
    auth,
    parties,
    assets,
    verification,
    email_processing,
    downloads,
    ec_dashboard,
    ec_user_management,
    party_admin,
    extension,
)

# Import models so SQLAlchemy creates their tables
import app.models.share_link  # noqa: F401
import app.models.geo_stats  # noqa: F401
import app.models.extension  # noqa: F401

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create tables on startup (use Alembic migrations in production)
    await init_db()

    # Start email polling if enabled
    email_task = None
    if settings.EMAIL_PROCESSING_ENABLED:
        from app.services.email_processor import email_polling_loop
        email_task = asyncio.create_task(email_polling_loop())
        logger.info("Email processing background task started")

    yield

    # Cancel email polling on shutdown
    if email_task:
        email_task.cancel()
        try:
            await email_task
        except asyncio.CancelledError:
            pass


app = FastAPI(
    title=settings.PROJECT_NAME,
    description=(
        "Verification system for political campaign images in the "
        "New Zealand 2026 General Election. Allows parties to register "
        "images and the public to verify their authenticity."
    ),
    version="0.1.0",
    lifespan=lifespan,
)

# CORS. Explicit method and header allowlist. Credentials are off
# because the API is bearer-token only (Authorization header). Local
# dev origins are only included outside production. Extra origins for
# staging or partner environments can be added through the
# CORS_EXTRA_ORIGINS setting (comma-separated).
_cors_origins: list[str] = []
if settings.PIVS_ENV.lower() in ("test", "development", "dev"):
    _cors_origins.extend(
        [
            "http://localhost:3000",
            "http://127.0.0.1:3000",
            "http://localhost",
            "http://127.0.0.1",
        ]
    )

if settings.VERIFICATION_BASE_URL:
    from urllib.parse import urlparse

    _parsed = urlparse(settings.VERIFICATION_BASE_URL)
    _origin = f"{_parsed.scheme}://{_parsed.netloc}".rstrip("/")
    if _origin not in _cors_origins:
        _cors_origins.append(_origin)
    _root = f"{_parsed.scheme}://{_parsed.hostname}"
    if _parsed.port:
        _root += f":{_parsed.port}"
    if _root not in _cors_origins:
        _cors_origins.append(_root)

if settings.CORS_EXTRA_ORIGINS:
    for o in settings.CORS_EXTRA_ORIGINS.split(","):
        o = o.strip().rstrip("/")
        if o and o not in _cors_origins:
            _cors_origins.append(o)

app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins,
    allow_credentials=False,
    allow_methods=["GET", "POST", "PATCH", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "X-Requested-With"],
    expose_headers=[
        "X-PIVS-Bloom-Items",
        "X-PIVS-Bloom-Bits",
        "X-PIVS-Bloom-Hashes",
        "X-PIVS-Bloom-Generated-At",
    ],
    max_age=3600,
)

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Catch unhandled exceptions so CORS headers are still included."""
    logger.error(f"Unhandled error on {request.method} {request.url.path}: {exc}")
    logger.error(traceback.format_exc())
    return JSONResponse(
        status_code=500,
        content={"detail": str(exc)},
    )


# Mount API routes
app.include_router(auth.router, prefix=settings.API_V1_PREFIX)
app.include_router(parties.router, prefix=settings.API_V1_PREFIX)
app.include_router(assets.router, prefix=settings.API_V1_PREFIX)
app.include_router(verification.router, prefix=settings.API_V1_PREFIX)
app.include_router(email_processing.router, prefix=settings.API_V1_PREFIX)
app.include_router(downloads.router, prefix=settings.API_V1_PREFIX)
app.include_router(ec_dashboard.router, prefix=settings.API_V1_PREFIX)
app.include_router(ec_user_management.router, prefix=settings.API_V1_PREFIX)
app.include_router(party_admin.router, prefix=settings.API_V1_PREFIX)
app.include_router(extension.router, prefix=settings.API_V1_PREFIX)


@app.get("/")
async def root():
    return {
        "name": settings.PROJECT_NAME,
        "version": "0.1.0",
        "docs": "/docs",
        "verify": f"{settings.API_V1_PREFIX}/verify",
    }


@app.get("/health")
async def health():
    return {"status": "ok", "version": "0.2.0", "build": "2025-02-16a"}
