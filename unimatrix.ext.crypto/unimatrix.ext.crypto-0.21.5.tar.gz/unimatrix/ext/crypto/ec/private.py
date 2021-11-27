"""Declares :class:`EllipticCurvePrivateKey`."""
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.asymmetric import utils

from .. import oid
from ..algorithms import SECP256K1SHA256
from ..algorithms import SECP256R1SHA256
from ..private import PrivateKey
from .public import EllipticCurvePublicKey


CURVE_CLASSMAP = {
    'P-256': ec.SECP256R1,
    'P-256K': ec.SECP256K1,
}


class EllipticCurvePrivateKey(PrivateKey):
    __algorithm_mapping = {
        'P-256K'    : oid.SECP256K1,
        'SECP256K1' : oid.SECP256K1,
        'P-256'     : oid.ECDSASHA256,
        'SECP256R1' : oid.ECDSASHA256,
    }

    capabilities = [
        SECP256K1SHA256,
        SECP256R1SHA256
    ]

    @property
    def curve(self):
        return self._key.curve

    @property
    def id(self) -> str:
        return self.keyid

    @property
    def keyid(self) -> str:
        return self.get_public_key().keyid

    @classmethod
    def fromkey(cls, key):
        return cls(key)

    @classmethod
    def generate(cls, curve):
        """Generate a new elliptic curve private key."""
        if isinstance(curve, str):
            curve = CURVE_CLASSMAP[curve]
        return cls(ec.generate_private_key(curve()))

    def __init__(self, key):
        self._key = key
        self._public = key.public_key()

    def setup(self, opts):
        pass

    def get_public_key(self) -> EllipticCurvePublicKey:
        return EllipticCurvePublicKey(self._public)

    def has_public_key(self) -> bool:
        """Return a boolean indicating if the private key is able to
        extract and provide its public key.
        """
        return True

    async def sign(self,
        digest: bytes,
        algorithm,
        *args, **kwargs
    ) -> bytes:
        """Returns the signature of byte-sequence `blob`, DER-encoded."""
        return self._key.sign(
            digest,
            ec.ECDSA(utils.Prehashed(algorithm))
        )

    def _get_key(self):
        return self._key
