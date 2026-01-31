"""
Dual hashing service: cryptographic (SHA-256) + perceptual (PDQ, pHash).

PDQ is Meta's open-source perceptual hash - 256-bit, tolerant of overlays,
compression, and resizing. Hamming distance <= 31 indicates a match.

pHash is a secondary perceptual hash for fallback matching.
"""

import hashlib
import io

import imagehash
import pdqhash
import numpy as np
from PIL import Image

from app.core.config import settings


def compute_sha256(image_bytes: bytes) -> str:
    """Compute SHA-256 cryptographic hash of raw image bytes."""
    return hashlib.sha256(image_bytes).hexdigest()


def compute_pdq(image_bytes: bytes) -> tuple[str, int]:
    """Compute PDQ perceptual hash. Returns (hash_hex, quality_score)."""
    img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    arr = np.array(img)
    hash_vector, quality = pdqhash.compute(arr)
    # Convert boolean array to hex string
    hash_hex = _bool_array_to_hex(hash_vector)
    return hash_hex, int(quality)


def compute_phash(image_bytes: bytes) -> str:
    """Compute pHash perceptual hash. Returns hex string."""
    img = Image.open(io.BytesIO(image_bytes))
    h = imagehash.phash(img)
    return str(h)


def compute_all_hashes(image_bytes: bytes) -> dict:
    """Compute all hashes for an image. Returns dict with all hash values."""
    sha256 = compute_sha256(image_bytes)
    pdq_hash, pdq_quality = compute_pdq(image_bytes)
    phash = compute_phash(image_bytes)
    return {
        "sha256": sha256,
        "pdq_hash": pdq_hash,
        "pdq_quality": pdq_quality,
        "phash": phash,
    }


def hamming_distance_hex(hash1: str, hash2: str) -> int:
    """Compute Hamming distance between two hex-encoded hashes."""
    b1 = int(hash1, 16)
    b2 = int(hash2, 16)
    xor = b1 ^ b2
    return bin(xor).count("1")


def pdq_match(hash1: str, hash2: str) -> tuple[bool, int]:
    """Check if two PDQ hashes match within threshold.
    Returns (is_match, distance)."""
    distance = hamming_distance_hex(hash1, hash2)
    return distance <= settings.PDQ_MATCH_THRESHOLD, distance


def phash_match(hash1: str, hash2: str) -> tuple[bool, int]:
    """Check if two pHash values match within threshold.
    Returns (is_match, distance)."""
    h1 = imagehash.hex_to_hash(hash1)
    h2 = imagehash.hex_to_hash(hash2)
    distance = h1 - h2
    return distance <= settings.PHASH_MATCH_THRESHOLD, distance


def _bool_array_to_hex(arr: np.ndarray) -> str:
    """Convert a boolean/bit array to a hex string."""
    flat = arr.flatten()
    # Pad to multiple of 4 for hex conversion
    padded_len = ((len(flat) + 3) // 4) * 4
    padded = np.zeros(padded_len, dtype=bool)
    padded[: len(flat)] = flat
    # Convert to hex
    hex_str = ""
    for i in range(0, len(padded), 4):
        nibble = (
            (int(padded[i]) << 3)
            | (int(padded[i + 1]) << 2)
            | (int(padded[i + 2]) << 1)
            | int(padded[i + 3])
        )
        hex_str += format(nibble, "x")
    return hex_str
