"""Tests for the encryption service."""

from app.services.encryption import (
    decrypt_data,
    decrypt_dek,
    decrypt_string,
    encrypt_data,
    encrypt_dek,
    encrypt_string,
    generate_dek,
)


class TestDEKGeneration:
    def test_generate_dek_returns_32_bytes(self):
        dek = generate_dek()
        assert len(dek) == 32

    def test_generate_dek_unique(self):
        dek1 = generate_dek()
        dek2 = generate_dek()
        assert dek1 != dek2


class TestDEKEncryption:
    def test_encrypt_decrypt_dek_roundtrip(self):
        dek = generate_dek()
        encrypted = encrypt_dek(dek)
        assert isinstance(encrypted, str)
        decrypted = decrypt_dek(encrypted)
        assert decrypted == dek

    def test_encrypted_dek_is_base64(self):
        import base64

        dek = generate_dek()
        encrypted = encrypt_dek(dek)
        # Should not raise
        base64.b64decode(encrypted)

    def test_different_encryptions_differ(self):
        dek = generate_dek()
        enc1 = encrypt_dek(dek)
        enc2 = encrypt_dek(dek)
        # Same DEK encrypted twice should differ (random nonce)
        assert enc1 != enc2


class TestDataEncryption:
    def test_encrypt_decrypt_roundtrip(self):
        dek = generate_dek()
        plaintext = b"This is secret image data" * 100
        ciphertext, nonce = encrypt_data(plaintext, dek)
        decrypted = decrypt_data(ciphertext, dek, nonce)
        assert decrypted == plaintext

    def test_ciphertext_differs_from_plaintext(self):
        dek = generate_dek()
        plaintext = b"Secret data"
        ciphertext, _ = encrypt_data(plaintext, dek)
        assert ciphertext != plaintext

    def test_wrong_key_fails(self):
        import pytest

        dek1 = generate_dek()
        dek2 = generate_dek()
        plaintext = b"Secret"
        ciphertext, nonce = encrypt_data(plaintext, dek1)
        with pytest.raises(Exception):
            decrypt_data(ciphertext, dek2, nonce)

    def test_wrong_nonce_fails(self):
        import os
        import pytest

        dek = generate_dek()
        plaintext = b"Secret"
        ciphertext, nonce = encrypt_data(plaintext, dek)
        wrong_nonce = os.urandom(12)
        with pytest.raises(Exception):
            decrypt_data(ciphertext, dek, wrong_nonce)


class TestStringEncryption:
    def test_encrypt_decrypt_string_roundtrip(self):
        original = "user@example.com"
        encrypted = encrypt_string(original)
        decrypted = decrypt_string(encrypted)
        assert decrypted == original

    def test_encrypted_string_not_readable(self):
        original = "sensitive@email.com"
        encrypted = encrypt_string(original)
        assert original not in encrypted

    def test_unicode_roundtrip(self):
        original = "Tēnā koe, NZ 🇳🇿"
        encrypted = encrypt_string(original)
        decrypted = decrypt_string(encrypted)
        assert decrypted == original

    def test_empty_string_roundtrip(self):
        encrypted = encrypt_string("")
        decrypted = decrypt_string(encrypted)
        assert decrypted == ""
