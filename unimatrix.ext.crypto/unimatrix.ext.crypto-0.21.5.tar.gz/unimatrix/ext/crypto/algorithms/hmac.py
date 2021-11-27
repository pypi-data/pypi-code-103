"""Declares Hash-Based Message Authentication Code (HMAC) algorithms."""
from .. import oid
from .signing import SigningAlgorithm


__all__ = [
    'HMACSHA224',
    'HMACSHA256',
    'HMACSHA384',
    'HMACSHA512',
]


class HMAC(SigningAlgorithm):

    def __init__(self, oid, algorithm):
        self.oid = oid
        self.algorithm = algorithm

    def digest(self, message):
        """Create a message digest using the configured hash algorithm."""
        return message

    def get_sign_parameters(self, key) -> dict:
        return {'algorithm': self.algorithm}

    def get_verify_parameters(self, key) -> dict:
        return {'algorithm': self.algorithm}

    def __hash__(self):
        return hash(f'hmac.{self.algorithm}')


HMACSHA224 = HMAC(oid.HMACSHA224, 'sha224')
HMACSHA256 = HMAC(oid.HMACSHA224, 'sha256')
HMACSHA384 = HMAC(oid.HMACSHA224, 'sha384')
HMACSHA512 = HMAC(oid.HMACSHA224, 'sha512')
