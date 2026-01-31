"""Tests for the local storage service."""

import os

import pytest

from app.services.storage import delete_blob, retrieve_blob, store_blob


class TestLocalStorage:
    @pytest.mark.asyncio
    async def test_store_and_retrieve(self):
        data = b"encrypted image data here"
        key = await store_blob(data, prefix="test_assets")
        assert key.startswith("test_assets/")

        retrieved = await retrieve_blob(key)
        assert retrieved == data

    @pytest.mark.asyncio
    async def test_store_creates_directories(self):
        data = b"some data"
        key = await store_blob(data, prefix="nested/deep/path")
        assert key.startswith("nested/deep/path/")
        retrieved = await retrieve_blob(key)
        assert retrieved == data

    @pytest.mark.asyncio
    async def test_delete_blob(self):
        data = b"to be deleted"
        key = await store_blob(data, prefix="test_delete")
        await delete_blob(key)

        with pytest.raises(FileNotFoundError):
            await retrieve_blob(key)

    @pytest.mark.asyncio
    async def test_unique_keys(self):
        data = b"same data"
        key1 = await store_blob(data, prefix="test_unique")
        key2 = await store_blob(data, prefix="test_unique")
        assert key1 != key2
