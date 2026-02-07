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
from app.api import auth, parties, assets, verification, email_processing

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

# CORS - allow the Next.js frontend (local dev + production)
_cors_origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost",
    "http://127.0.0.1",
]
# In production behind nginx, the public origin is needed for direct API calls
if settings.VERIFICATION_BASE_URL:
    from urllib.parse import urlparse
    _parsed = urlparse(settings.VERIFICATION_BASE_URL)
    _origin = f"{_parsed.scheme}://{_parsed.netloc}".rstrip("/")
    if _origin not in _cors_origins:
        _cors_origins.append(_origin)
    # Also add the root (without /verify path)
    _root = f"{_parsed.scheme}://{_parsed.hostname}"
    if _parsed.port:
        _root += f":{_parsed.port}"
    if _root not in _cors_origins:
        _cors_origins.append(_root)

app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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
    return {"status": "ok"}
