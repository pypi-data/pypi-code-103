# pylint: skip-file
from unimatrix.ext.crypto import algorithms
from ..ec import EllipticCurvePrivateKey
from .base import SigningTestCase


class SECP256R1SHA256TestCase(SigningTestCase):
    __test__ = True
    algorithm = algorithms.SECP256R1SHA256

    def get_data(self, *args, **kwargs):
        return self.algorithm.digest(super().get_data(*args, **kwargs))

    def get_private_key(self):
        return EllipticCurvePrivateKey.generate(self.algorithm.curve)


class SECP256K1SHA256TestCase(SECP256R1SHA256TestCase):
    __test__ = True
    algorithm = algorithms.SECP256K1SHA256
