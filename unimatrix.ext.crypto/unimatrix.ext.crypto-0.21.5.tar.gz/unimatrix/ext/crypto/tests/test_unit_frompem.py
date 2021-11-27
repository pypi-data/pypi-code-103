# pylint: skip-file
import unittest

from unimatrix.ext import crypto
from unimatrix.ext.crypto.ec import EllipticCurvePrivateKey
from unimatrix.ext.crypto.pkcs import RSAPrivateKey


class ECDeserializationTestCase(unittest.TestCase):

    def setUp(self):
        self.key = EllipticCurvePrivateKey.generate('P-256')
        self.pub = self.key.get_public_key()

    def test_private(self):
        key = crypto.frompem(self.key.pem)
        self.assertEqual(key.keyid, self.key.keyid)

    def test_public(self):
        pub = crypto.frompem(self.pub.pem)
        self.assertEqual(pub.keyid, self.pub.keyid)


class RSADeserializationTestCase(ECDeserializationTestCase):

    def setUp(self):
        self.key = RSAPrivateKey.generate(512)
        self.pub = self.key.get_public_key()
    
