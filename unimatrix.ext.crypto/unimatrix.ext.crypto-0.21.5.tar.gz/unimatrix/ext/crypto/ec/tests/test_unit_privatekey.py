# pylint: skip-file
import asyncio
import hashlib
import unittest

import secp256k1
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.asymmetric.utils import decode_dss_signature

from ...signer import GenericSigner
from ...algorithms import SECP256K1SHA256
from .. import EllipticCurvePrivateKey


class EllipticCurvePrivateKeyTestCase(unittest.TestCase):

    def setUp(self):
        self.algorithm = SECP256K1SHA256
        self.private = EllipticCurvePrivateKey.generate(self.algorithm.curve)
        self.public = self.private.get_public_key()

    def test_sign_and_verify(self):
        buf = hashlib.sha256(b'foo').digest()
        sig = asyncio.run(self.algorithm.sign(self.private, buf))
        pub = self.private.get_public_key()
        self.algorithm.verify(pub, sig, buf)

    def test_sign_and_verify_with_secp256k1(self):
        buf = hashlib.sha256(b'foo').digest()
        pub = secp256k1.PublicKey(
            bytes(self.private.get_public_key()), raw=True)
        sig = pub.ecdsa_deserialize(
            bytes(asyncio.run(self.algorithm.sign(self.private, buf)))
        )
        self.assertTrue(pub.ecdsa_verify(hashlib.sha256(b'foo').digest(),
            sig, raw=True))

    def test_sign_and_verify_with_secp256k1_signer(self):
        digest = hashlib.sha256(b'foo').digest()
        signer = GenericSigner(SECP256K1SHA256, self.private)
        sig = asyncio.run(signer.sign(digest))
        res = sig.verify(signer.get_public_key(), digest)
