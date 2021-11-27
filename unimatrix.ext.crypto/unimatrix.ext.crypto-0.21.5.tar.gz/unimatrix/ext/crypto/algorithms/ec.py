# pylint: disable=line-too-long
"""Declares Elliptic Curve (EC) algorithms."""
from cryptography.hazmat.primitives.asymmetric.utils import decode_dss_signature
from cryptography.hazmat.primitives.asymmetric.utils import encode_dss_signature
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import hashes

from .. import oid
from ..signature import Signature
from .signing import SigningAlgorithm


__all__ = [
    'SECP256K1SHA256',
    'SECP256R1SHA256',
]


class ECDSA(SigningAlgorithm):
    __module__ = 'unimatrix.ext.crypto.algorithms'

    class ECDSASignature(Signature):

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.r, self.s = decode_dss_signature(bytes(self))
            self.raw = b''
            self.raw += int.to_bytes(self.r, 32, 'big')
            self.raw += int.to_bytes(self.s, 32, 'big')

    signature_class = ECDSASignature

    def __init__(self, oid, curve, hashfunc):
        self.oid = oid
        self.curve = curve
        self.hashfunc = hashfunc

    def get_sign_parameters(self, key) -> dict:
        algorithm = self.hashfunc()
        return {
            'algorithm': algorithm,
            'hasher': hashes.Hash(algorithm),
            'curve': self.curve()
        }

    def get_verify_parameters(self, key) -> dict:
        algorithm = self.hashfunc()
        return {
            'algorithm': algorithm,
            'hasher': hashes.Hash(algorithm),
            'curve': self.curve()
        }

    def __eq__(self, algorithm):
        curve = getattr(algorithm, 'curve', None)
        hashfunc = getattr(algorithm, 'hashfunc', None)
        return (self.curve == curve) and (self.hashfunc == hashfunc)

    def __hash__(self):
        return hash(f'{self.curve.__name__}.{self.hashfunc.__name__}')


class SECP256K1(ECDSA):
    __module__ = 'unimatrix.ext.crypto.algorithms'
    curve_order = 115792089237316195423570985008687907852837564279074904382605163141518161494337
    half_order = 57896044618658097711785492504343953926418782139537452191302581570759080747168

    def normalize_signature(self, sig):
        r, s = decode_dss_signature(sig)
        if s > self.half_order:
            s = self.curve_order - s
        sig = bytearray()
        return encode_dss_signature(r, s)


SECP256K1SHA256 = SECP256K1(oid.SECP256K1, ec.SECP256K1, hashes.SHA256)
SECP256R1SHA256 = ECDSA(oid.ECDSA, ec.SECP256R1, hashes.SHA256)
