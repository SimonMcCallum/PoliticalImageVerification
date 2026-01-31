"""
NZ Political Image Verification System - API Server

FastAPI application that provides:
- Public verification API (no auth required)
- Party asset submission API (authenticated)
- Party management API (admin only)
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import init_db
from app.api import auth, parties, assets, verification


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create tables on startup (use Alembic migrations in production)
    await init_db()
    yield


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

# CORS - allow the Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API routes
app.include_router(auth.router, prefix=settings.API_V1_PREFIX)
app.include_router(parties.router, prefix=settings.API_V1_PREFIX)
app.include_router(assets.router, prefix=settings.API_V1_PREFIX)
app.include_router(verification.router, prefix=settings.API_V1_PREFIX)


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
