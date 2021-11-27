# pylint: skip-file
import unittest

from cryptography.hazmat.primitives.asymmetric import ec

from ..ec import EllipticCurvePrivateKey
from ..pkcs import RSAPrivateKey


class SECP256R1TestCase(unittest.TestCase):
    key_class = EllipticCurvePrivateKey
    curve = ec.SECP256R1

    def setUp(self):
        self.key = self.generate_key()
        self.pub = self.key.get_public_key()
        self.pub_jwk = self.pub.jwk

    def generate_key(self):
        return self.key_class.generate(self.curve)

    def test_fromjwk_public(self):
        k = self.pub.fromjwk(self.pub_jwk)
        self.assertEqual(self.pub.keyid, k.keyid)


class SECP256K1TestCase(SECP256R1TestCase):
    key_class = EllipticCurvePrivateKey
    curve = ec.SECP256K1


class RSATestCase(SECP256R1TestCase):
    key_class = RSAPrivateKey

    def generate_key(self):
        return self.key_class.generate()
