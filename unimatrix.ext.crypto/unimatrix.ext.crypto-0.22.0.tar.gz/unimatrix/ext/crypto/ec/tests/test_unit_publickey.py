# pylint: skip-file
import unittest

from cryptography.hazmat.primitives.asymmetric import ec

from .. import EllipticCurvePublicKey


class PublicKeyTestCase(unittest.TestCase):

    def setUp(self):
        self.key = ec.generate_private_key(ec.SECP256K1())
        self.public = EllipticCurvePublicKey(self.key.public_key())

    def test_bytes(self):
        bytes(self.public)

