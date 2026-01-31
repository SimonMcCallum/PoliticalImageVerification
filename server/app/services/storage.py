"""
Storage service for encrypted image blobs.
Supports local filesystem (dev) and S3-compatible (production).
"""

import os
import uuid
from pathlib import Path

import aiofiles

from app.core.config import settings


async def store_blob(data: bytes, prefix: str = "assets") -> str:
    """Store an encrypted blob and return its storage key."""
    if settings.STORAGE_BACKEND == "local":
        return await _store_local(data, prefix)
    else:
        return await _store_s3(data, prefix)


async def retrieve_blob(storage_key: str) -> bytes:
    """Retrieve an encrypted blob by storage key."""
    if settings.STORAGE_BACKEND == "local":
        return await _retrieve_local(storage_key)
    else:
        return await _retrieve_s3(storage_key)


async def delete_blob(storage_key: str) -> None:
    """Delete a blob by storage key."""
    if settings.STORAGE_BACKEND == "local":
        await _delete_local(storage_key)
    else:
        await _delete_s3(storage_key)


# --- Local filesystem storage ---


async def _store_local(data: bytes, prefix: str) -> str:
    base_path = Path(settings.LOCAL_STORAGE_PATH) / prefix
    base_path.mkdir(parents=True, exist_ok=True)
    filename = f"{uuid.uuid4().hex}"
    file_path = base_path / filename
    async with aiofiles.open(file_path, "wb") as f:
        await f.write(data)
    return f"{prefix}/{filename}"


async def _retrieve_local(storage_key: str) -> bytes:
    file_path = Path(settings.LOCAL_STORAGE_PATH) / storage_key
    async with aiofiles.open(file_path, "rb") as f:
        return await f.read()


async def _delete_local(storage_key: str) -> None:
    file_path = Path(settings.LOCAL_STORAGE_PATH) / storage_key
    if file_path.exists():
        os.remove(file_path)


# --- S3-compatible storage (placeholder for production) ---


async def _store_s3(data: bytes, prefix: str) -> str:
    raise NotImplementedError("S3 storage not yet configured. Set STORAGE_BACKEND=local for development.")


async def _retrieve_s3(storage_key: str) -> bytes:
    raise NotImplementedError("S3 storage not yet configured.")


async def _delete_s3(storage_key: str) -> None:
    raise NotImplementedError("S3 storage not yet configured.")
