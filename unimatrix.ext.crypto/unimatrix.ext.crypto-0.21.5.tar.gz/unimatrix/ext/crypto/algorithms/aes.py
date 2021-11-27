"""Supplies Advanced Encryption Standard (AES) algorithms."""
import os
import hashlib

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from .. import oid
from ..ciphertext import Ciphertext
from ..plaintext import Plaintext
from .encryption import AuthenticatedEncryptionAlgorithm


__all__ = [
    'AES256GCM'
]


class AESGCM(AuthenticatedEncryptionAlgorithm):
    cipher_class = AESGCM
    nonce_length = 12 # 96-bit nonce length recommended by nist
    IncompatibleKey = type('IncompatibleKey', (Exception,), {})

    def __init__(self, oid, kdf):
        self.oid = oid
        self.kdf = kdf

    def pre_encrypt(self, key, pt):
        if not hasattr(pt, 'nonce'):
            pt.nonce = os.urandom(self.nonce_length)
        if not hasattr(pt, 'aad'):
            pt.aad = b''

    async def apply_decrypt(self, secret: bytes, ct: Ciphertext) -> Plaintext:
        cipher = self.cipher_class(self.kdf(secret))
        return cipher.decrypt(ct.nonce, bytes(ct), ct.aad)

    async def apply_encrypt(self, secret: bytes, pt: Plaintext) -> bytes:
        """Applies the configured cipher class using the given secret, nonce
        plaintext and Additional authenticated data (AAD).
        """
        cipher = self.cipher_class(self.kdf(secret))
        return cipher.encrypt(pt.nonce, bytes(pt), pt.aad)

    async def encrypt(self, key, pt: Plaintext, *args, **kwargs) -> Ciphertext:
        return await super().encrypt(key, pt, *args, **kwargs)

    def get_encrypt_parameters(self, key, pt) -> dict:
        return {
            'apply_encrypt': self.apply_encrypt
        }

    def get_decrypt_parameters(self, key, ct) -> dict:
        return {
            'apply_decrypt': self.apply_decrypt,
        }


AES256GCM = AESGCM(oid.AES256GCM, lambda x: hashlib.sha256(x).digest())
