"""AES-256-GCM encryption for note taker. Uses PBKDF2-SHA256 key derivation."""

import os
import struct
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes

PBKDF2_ITERATIONS = 100_000
SALT_SIZE = 16   # bytes
NONCE_SIZE = 12  # bytes for AES-GCM

def derive_key(password: str, salt: bytes) -> bytes:
    """Derive a 256-bit AES key from password + salt using PBKDF2-SHA256."""
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=PBKDF2_ITERATIONS,
    )
    return kdf.derive(password.encode("utf-8"))

def encrypt_data(data: bytes, password: str) -> bytes:
    """Encrypt bytes with AES-256-GCM. Returns: salt(16) + nonce(12) + ciphertext."""
    salt = os.urandom(SALT_SIZE)
    nonce = os.urandom(NONCE_SIZE)
    key = derive_key(password, salt)
    aesgcm = AESGCM(key)
    ciphertext = aesgcm.encrypt(nonce, data, None)
    return salt + nonce + ciphertext

def decrypt_data(blob: bytes, password: str) -> bytes:
    """Decrypt bytes produced by encrypt_data. Raises ValueError on wrong password."""
    if len(blob) < SALT_SIZE + NONCE_SIZE:
        raise ValueError("Invalid encrypted data: too short")
    salt = blob[:SALT_SIZE]
    nonce = blob[SALT_SIZE:SALT_SIZE + NONCE_SIZE]
    ciphertext = blob[SALT_SIZE + NONCE_SIZE:]
    key = derive_key(password, salt)
    aesgcm = AESGCM(key)
    try:
        return aesgcm.decrypt(nonce, ciphertext, None)
    except Exception:
        raise ValueError("Wrong password or corrupted data")
