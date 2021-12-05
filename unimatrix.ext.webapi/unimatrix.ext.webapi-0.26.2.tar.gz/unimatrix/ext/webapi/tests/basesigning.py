# pylint: skip-file
import asyncio
import unittest

from cryptography.hazmat.primitives.asymmetric import ec
from unimatrix.ext import crypto
from unimatrix.ext import jose
from unimatrix.ext.crypto.ec import EllipticCurvePrivateKey
from unimatrix.lib.datastructures import DTO


class BaseSigningTestCase(unittest.TestCase):

    def generate_key(self):
        private_key = ec.generate_private_key(ec.SECP256K1())\
            .private_numbers()\
            .private_value
        return EllipticCurvePrivateKey(DTO(secret=private_key))

    def get_signer(self, key):
        return crypto.GenericSigner(crypto.SECP256K1SHA256, key)

    def get_token(self, key, **claims):
        signer = self.get_signer(key)
        token = asyncio.run(jose.jwt(claims, signer=signer))
        asyncio.run(jose.parse(bytes(token)).verify(key.get_public_key()))
        return str(token)

    def parse_token(self, token: str) -> dict:
        return DTO(dict(jose.parse(str.encode(token)).payload))

    def trust(self, key):
        public = key.get_public_key()
        crypto.trust.register(crypto.TrustedPublicKey(public))
        return public.keyid

    def tearDown(self):
        crypto.trust.clear()
