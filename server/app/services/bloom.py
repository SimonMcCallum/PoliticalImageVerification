"""Bloom filter generator for the extension snapshot.

The wire format must stay byte-compatible with
``extension/src/lib/bloom/bloom.ts``:

  bytes 0..3   magic "PIBF"
  byte  4      version 1
  byte  5      reserved (0)
  bytes 6..9   numBits (uint32 LE)
  bytes 10..11 numHashes k (uint16 LE)
  bytes 12..19 itemCount (uint64 LE)
  bytes 20..27 generatedAt millis (uint64 LE)
  bytes 28..   bit array (LSB-first within each byte)

Hashing strategy mirrors the JS: two base hashes (FNV-1a and djb2)
combined via Kirsch-Mitzenmacher.
"""

from __future__ import annotations

import math
import struct
import time
from dataclasses import dataclass

MAGIC = b"PIBF"
VERSION = 1
HEADER_BYTES = 28


def _fnv1a_32(s: str) -> int:
    h = 0x811C9DC5
    for ch in s.encode("utf-8"):
        h ^= ch
        h = (h * 0x01000193) & 0xFFFFFFFF
    return h


def _djb2_32(s: str) -> int:
    h = 5381
    for ch in s.encode("utf-8"):
        h = (h * 33 + ch) & 0xFFFFFFFF
    return h


def _base_hashes(s: str) -> tuple[int, int]:
    return _fnv1a_32(s), _djb2_32(s)


def _combine(h1: int, h2: int, i: int, mod: int) -> int:
    return ((h1 + i * h2) & 0xFFFFFFFF) % mod


@dataclass
class BloomFilter:
    num_bits: int
    num_hashes: int
    bits: bytearray
    item_count: int = 0
    generated_at_millis: int = 0

    @classmethod
    def for_items(cls, expected_items: int, fpr: float) -> "BloomFilter":
        if expected_items <= 0:
            raise ValueError("expected_items must be > 0")
        if not (0.0 < fpr < 1.0):
            raise ValueError("fpr must be in (0, 1)")
        ln2 = math.log(2)
        num_bits = max(8, math.ceil(-(expected_items * math.log(fpr)) / (ln2 * ln2)))
        num_hashes = max(1, round((num_bits / expected_items) * ln2))
        return cls(num_bits=num_bits, num_hashes=num_hashes, bits=bytearray((num_bits + 7) // 8))

    def add(self, hex_string: str) -> None:
        h1, h2 = _base_hashes(hex_string)
        for i in range(self.num_hashes):
            idx = _combine(h1, h2, i, self.num_bits)
            self.bits[idx >> 3] |= 1 << (idx & 7)
        self.item_count += 1

    def might_contain(self, hex_string: str) -> bool:
        h1, h2 = _base_hashes(hex_string)
        for i in range(self.num_hashes):
            idx = _combine(h1, h2, i, self.num_bits)
            if not (self.bits[idx >> 3] & (1 << (idx & 7))):
                return False
        return True

    def serialize(self) -> bytes:
        if not self.generated_at_millis:
            self.generated_at_millis = int(time.time() * 1000)
        out = bytearray(HEADER_BYTES + len(self.bits))
        out[0:4] = MAGIC
        out[4] = VERSION
        out[5] = 0
        struct.pack_into("<I", out, 6, self.num_bits)
        struct.pack_into("<H", out, 10, self.num_hashes)
        struct.pack_into("<Q", out, 12, self.item_count)
        struct.pack_into("<Q", out, 20, self.generated_at_millis)
        out[HEADER_BYTES:] = self.bits
        return bytes(out)
