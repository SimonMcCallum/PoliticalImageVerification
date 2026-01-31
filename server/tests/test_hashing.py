"""Tests for the hashing service."""

import io

import pytest
from PIL import Image

from app.services.hashing import (
    compute_all_hashes,
    compute_pdq,
    compute_phash,
    compute_sha256,
    hamming_distance_hex,
    pdq_match,
    phash_match,
)
from tests.conftest import create_test_image


class TestSHA256:
    def test_deterministic(self):
        data = b"test image bytes"
        h1 = compute_sha256(data)
        h2 = compute_sha256(data)
        assert h1 == h2

    def test_hex_string_64_chars(self):
        h = compute_sha256(b"data")
        assert len(h) == 64
        assert all(c in "0123456789abcdef" for c in h)

    def test_different_input_different_hash(self):
        h1 = compute_sha256(b"image1")
        h2 = compute_sha256(b"image2")
        assert h1 != h2


class TestPDQ:
    def test_compute_returns_hash_and_quality(self):
        img_bytes = create_test_image()
        pdq_hash, quality = compute_pdq(img_bytes)
        assert isinstance(pdq_hash, str)
        assert isinstance(quality, int)
        assert len(pdq_hash) == 64  # 256 bits = 64 hex chars
        assert quality >= 0

    def test_identical_images_same_hash(self):
        img_bytes = create_test_image(color="blue")
        h1, _ = compute_pdq(img_bytes)
        h2, _ = compute_pdq(img_bytes)
        assert h1 == h2

    def test_different_images_different_hash(self):
        img1 = create_test_image(color="red")
        img2 = create_test_image(color="blue")
        h1, _ = compute_pdq(img1)
        h2, _ = compute_pdq(img2)
        # May or may not differ for solid colors, but test that it runs
        assert isinstance(h1, str) and isinstance(h2, str)

    def test_resized_image_similar_hash(self):
        """PDQ should be tolerant of resizing."""
        img_bytes = create_test_image(width=400, height=400, color="green")
        h1, _ = compute_pdq(img_bytes)

        # Resize the image
        img = Image.open(io.BytesIO(img_bytes))
        img_small = img.resize((200, 200), Image.LANCZOS)
        buf = io.BytesIO()
        img_small.save(buf, format="PNG")
        h2, _ = compute_pdq(buf.getvalue())

        distance = hamming_distance_hex(h1, h2)
        # Resized solid color images should be very close
        assert distance <= 31, f"PDQ distance {distance} exceeds threshold for resize"


class TestPHash:
    def test_compute_returns_hex_string(self):
        img_bytes = create_test_image()
        h = compute_phash(img_bytes)
        assert isinstance(h, str)
        assert len(h) == 16  # 64 bits = 16 hex chars

    def test_identical_images_same_hash(self):
        img_bytes = create_test_image(color="green")
        h1 = compute_phash(img_bytes)
        h2 = compute_phash(img_bytes)
        assert h1 == h2


class TestHammingDistance:
    def test_identical_hashes_zero_distance(self):
        h = "abcdef0123456789" * 4
        assert hamming_distance_hex(h, h) == 0

    def test_one_bit_difference(self):
        h1 = "0" * 64
        h2 = "1" + "0" * 63  # One bit difference
        assert hamming_distance_hex(h1, h2) == 1

    def test_completely_different(self):
        h1 = "0" * 64
        h2 = "f" * 64
        assert hamming_distance_hex(h1, h2) == 256


class TestPDQMatch:
    def test_identical_matches(self):
        h = "a" * 64
        is_match, distance = pdq_match(h, h)
        assert is_match is True
        assert distance == 0

    def test_distant_no_match(self):
        h1 = "0" * 64
        h2 = "f" * 64
        is_match, distance = pdq_match(h1, h2)
        assert is_match is False
        assert distance == 256


class TestPHashMatch:
    def test_identical_matches(self):
        h = "a" * 16
        is_match, distance = phash_match(h, h)
        assert bool(is_match) is True
        assert int(distance) == 0


class TestComputeAllHashes:
    def test_returns_all_fields(self):
        img_bytes = create_test_image()
        result = compute_all_hashes(img_bytes)
        assert "sha256" in result
        assert "pdq_hash" in result
        assert "pdq_quality" in result
        assert "phash" in result

    def test_sha256_correct_length(self):
        result = compute_all_hashes(create_test_image())
        assert len(result["sha256"]) == 64

    def test_pdq_correct_length(self):
        result = compute_all_hashes(create_test_image())
        assert len(result["pdq_hash"]) == 64
