"""Tests for crypto.py — AES-256-GCM encryption module."""
import unittest

class TestCrypto(unittest.TestCase):
    def test_encrypt_decrypt_roundtrip(self):
        from crypto import encrypt_data, decrypt_data
        data = b"hello world"
        blob = encrypt_data(data, "mypassword")
        result = decrypt_data(blob, "mypassword")
        self.assertEqual(result, data)

    def test_wrong_password_raises(self):
        from crypto import encrypt_data, decrypt_data
        blob = encrypt_data(b"secret", "correct")
        with self.assertRaises(ValueError):
            decrypt_data(blob, "wrong")

    def test_each_encrypt_produces_different_blob(self):
        """Same data + password must produce different ciphertext (random salt/nonce)."""
        from crypto import encrypt_data
        blob1 = encrypt_data(b"data", "pass")
        blob2 = encrypt_data(b"data", "pass")
        self.assertNotEqual(blob1, blob2)

    def test_empty_data_encrypts_and_decrypts(self):
        from crypto import encrypt_data, decrypt_data
        blob = encrypt_data(b"", "pass")
        result = decrypt_data(blob, "pass")
        self.assertEqual(result, b"")

    def test_unicode_password(self):
        from crypto import encrypt_data, decrypt_data
        blob = encrypt_data(b"note content", "ລະຫັດລ້ານ")
        result = decrypt_data(blob, "ລະຫັດລ້ານ")
        self.assertEqual(result, b"note content")

    def test_corrupted_data_raises(self):
        from crypto import encrypt_data, decrypt_data
        blob = bytearray(encrypt_data(b"data", "pass"))
        blob[-1] ^= 0xFF  # flip last byte
        with self.assertRaises(ValueError):
            decrypt_data(bytes(blob), "pass")

    def test_truncated_data_raises(self):
        from crypto import decrypt_data
        with self.assertRaises(ValueError):
            decrypt_data(b"tooshort", "pass")
