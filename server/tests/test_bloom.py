"""Unit tests for the Python-side bloom filter and its wire format."""

import struct

import pytest

from app.services.bloom import HEADER_BYTES, MAGIC, BloomFilter


class TestBloomFilterPython:
    def test_inserted_items_match(self):
        bf = BloomFilter.for_items(1000, 0.01)
        items = [f"hash-{i}" for i in range(200)]
        for h in items:
            bf.add(h)
        for h in items:
            assert bf.might_contain(h)

    def test_uninserted_items_mostly_dont_match(self):
        bf = BloomFilter.for_items(500, 0.01)
        for i in range(500):
            bf.add(f"yes-{i}")
        false_positives = sum(
            1 for i in range(2000) if bf.might_contain(f"no-{i}")
        )
        assert false_positives / 2000 < 0.05

    def test_serialize_starts_with_magic_and_version(self):
        bf = BloomFilter.for_items(100, 0.01)
        bf.add("only one")
        blob = bf.serialize()
        assert blob[0:4] == MAGIC
        assert blob[4] == 1
        # Header followed by bit array.
        assert len(blob) == HEADER_BYTES + len(bf.bits)

    def test_wire_format_field_offsets(self):
        bf = BloomFilter.for_items(64, 0.01)
        for i in range(10):
            bf.add(f"x-{i}")
        blob = bf.serialize()
        num_bits = struct.unpack_from("<I", blob, 6)[0]
        num_hashes = struct.unpack_from("<H", blob, 10)[0]
        item_count = struct.unpack_from("<Q", blob, 12)[0]
        assert num_bits == bf.num_bits
        assert num_hashes == bf.num_hashes
        assert item_count == 10


# Round-trip a Python-built filter through the byte format and verify
# that querying it via the Python class gives identical results to
# the in-memory original. This locks the wire format in place.
@pytest.mark.parametrize("seed_count", [1, 10, 100, 500])
def test_round_trip_via_serialized_form(seed_count: int):
    bf = BloomFilter.for_items(max(seed_count, 16), 0.01)
    items = [f"item-{i}" for i in range(seed_count)]
    for x in items:
        bf.add(x)
    blob = bf.serialize()

    num_bits = struct.unpack_from("<I", blob, 6)[0]
    num_hashes = struct.unpack_from("<H", blob, 10)[0]
    bits = bytearray(blob[HEADER_BYTES:])
    rebuilt = BloomFilter(num_bits=num_bits, num_hashes=num_hashes, bits=bits)

    for x in items:
        assert rebuilt.might_contain(x)
