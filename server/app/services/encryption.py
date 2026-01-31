"""
Encryption service using AES-256-GCM with envelope encryption.

Each asset gets a unique Data Encryption Key (DEK).
The DEK is encrypted by the master Key Encryption Key (KEK).
In production, the KEK should live in an HSM or cloud KMS.
"""

import base64
import os

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from app.core.config import settings


def _get_kek() -> bytes:
    return bytes.fromhex(settings.MASTER_ENCRYPTION_KEY)


def generate_dek() -> bytes:
    return AESGCM.generate_key(bit_length=256)


def encrypt_dek(dek: bytes) -> str:
    kek = _get_kek()
    aes = AESGCM(kek)
    nonce = os.urandom(12)
    encrypted = aes.encrypt(nonce, dek, None)
    return base64.b64encode(nonce + encrypted).decode("utf-8")


def decrypt_dek(encrypted_dek_b64: str) -> bytes:
    kek = _get_kek()
    raw = base64.b64decode(encrypted_dek_b64)
    nonce = raw[:12]
    ciphertext = raw[12:]
    aes = AESGCM(kek)
    return aes.decrypt(nonce, ciphertext, None)


def encrypt_data(data: bytes, dek: bytes) -> tuple[bytes, bytes]:
    """Encrypt data with DEK. Returns (ciphertext, iv/nonce)."""
    aes = AESGCM(dek)
    nonce = os.urandom(12)
    ciphertext = aes.encrypt(nonce, data, None)
    return ciphertext, nonce


def decrypt_data(ciphertext: bytes, dek: bytes, nonce: bytes) -> bytes:
    """Decrypt data with DEK and nonce."""
    aes = AESGCM(dek)
    return aes.decrypt(nonce, ciphertext, None)


def encrypt_string(plaintext: str) -> str:
    """Encrypt a string field (email, filename, etc.) using the master KEK directly.
    Returns base64-encoded nonce+ciphertext."""
    kek = _get_kek()
    aes = AESGCM(kek)
    nonce = os.urandom(12)
    ciphertext = aes.encrypt(nonce, plaintext.encode("utf-8"), None)
    return base64.b64encode(nonce + ciphertext).decode("utf-8")


def decrypt_string(encrypted_b64: str) -> str:
    """Decrypt a string field encrypted with encrypt_string."""
    kek = _get_kek()
    raw = base64.b64decode(encrypted_b64)
    nonce = raw[:12]
    ciphertext = raw[12:]
    aes = AESGCM(kek)
    return aes.decrypt(nonce, ciphertext, None).decode("utf-8")
