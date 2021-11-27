"""Declares :class:`EllipticCurvePublicKey`."""
import base64
import hashlib

from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import serialization

from ..public import PublicKey
from .verifier import EllipticCurveVerifier


CRV_CLASSMAP = {
    'P-256': ec.SECP256R1,
    'P-256K': ec.SECP256K1,
    ec.SECP256R1: 'P-256',
    ec.SECP256K1: 'P-256K',
}


class EllipticCurvePublicKey(EllipticCurveVerifier, PublicKey):

    @property
    def curve(self):
        return type(self._public.curve)

    @property
    def jwk(self) -> dict:
        x = base64.urlsafe_b64encode(
            int.to_bytes(self.x, 32, 'big')
        )
        y = base64.urlsafe_b64encode(
            int.to_bytes(self.y, 32, 'big')
        )
        return {
            "kty": "EC",
            "crv": CRV_CLASSMAP[self.curve],
            'kid': self.keyid,
            'x': bytes.decode(x),
            'y': bytes.decode(y),
        }

    @property
    def keyid(self):
        return hashlib.md5(bytes(self)).hexdigest() # nosec

    @property
    def y(self):
        return self._numbers.y

    @property
    def x(self):
        return self._numbers.x

    @property
    def public(self):
        return self._public

    @classmethod
    def fromjwk(cls, jwk: dict):
        return cls.fromnumbers(
            int.from_bytes(
                base64.urlsafe_b64decode(str.encode(jwk['x'])), 'big'
            ),
            int.from_bytes(
                base64.urlsafe_b64decode(str.encode(jwk['y'])), 'big'
            ),
            curve=CRV_CLASSMAP[ jwk['crv'] ]()
        )

    @classmethod
    def fromnumbers(cls, x, y, curve):
        assert isinstance(x, int) # nosec
        assert isinstance(y, int) # nosec
        return cls(ec.EllipticCurvePublicNumbers(x, y, curve).public_key())

    @classmethod
    def frompem(cls, pem):
        if isinstance(pem, str):
            pem = str.encode(pem)
        return cls(serialization.load_pem_public_key(pem))

    def __init__(self, key, capabilities=None):
        self._public = key
        self._numbers = self._public.public_numbers()
        self.capabilities = capabilities or self.capabilities

    async def encrypt(self, *args, **kwargs):
        raise NotImplementedError

    def __bytes__(self):
        buf = bytearray()
        buf.append(0x04)
        buf.extend(int.to_bytes(self._numbers.x, 32, 'big'))
        buf.extend(int.to_bytes(self._numbers.y, 32, 'big'))
        return bytes(buf)
