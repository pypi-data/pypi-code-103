"""Declares :class:`PKCSPublic`."""
from cryptography.hazmat.primitives.asymmetric import utils
from cryptography.exceptions import InvalidSignature

from ..public import PublicKey
from .base import PKCSObject


class PKCSPublic(PKCSObject, PublicKey):

    def encrypt(self, pt, padding):
        return self._public.encrypt(bytes(pt), padding)

    def verify(self, signature: bytes, digest: bytes,
        padding, algorithm, prehashed=True, *args, **kwargs) -> bytes:
        algorithm = utils.Prehashed(algorithm)
        if not prehashed:
            raise NotImplementedError
        try:
            self._public.verify(bytes(signature), digest, padding, algorithm)
            return True
        except InvalidSignature:
            return False

