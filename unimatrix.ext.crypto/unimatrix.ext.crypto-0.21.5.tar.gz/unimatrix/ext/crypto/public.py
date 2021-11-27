"""Declares :class:`PublicKey`."""
import abc

from cryptography.hazmat.primitives import serialization


class PublicKey(metaclass=abc.ABCMeta):
    """Declares the interface for public key."""
    capabilities = []

    @property
    def bytes(self) -> bytes:
        """Return a byte sequence holding the public key."""
        raise NotImplementedError

    @property
    def id(self) -> str:
        return self.keyid

    @property
    def jwk(self) -> dict:
        """Return a dictionary in the JSON Web Key format."""
        raise NotImplementedError

    @property
    def keyid(self) -> str:
        """Return the key identifier."""
        raise NotImplementedError

    @property
    def pem(self) -> bytes:
        """Return a byte-sequence holding the PEM-encoded key,
        if supported.
        """
        return self._public.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )

    @classmethod
    def fromjwk(self, *args, **kwargs):
        raise NotImplementedError

    @classmethod
    def fromnumbers(self, *args, **kwargs):
        raise NotImplementedError

    @classmethod
    def fromkey(cls, key):
        return cls(key)

    def is_private(self) -> bool:
        """Return a boolean indicating if the key is private."""
        return False

    def is_public(self) -> bool:
        """Return a boolean indicating if the key is public."""
        return True

    async def can_use(self, oid: str) -> bool:
        """Return a boolean if the key can use the algorithm identified by
        the provided `oid`.
        """
        raise NotImplementedError

    async def encrypt(self, pt: bytes, *args, **kwargs) -> bytes:
        """Encrypt byte-sequence `pt` using the specified parameters."""
        raise NotImplementedError

    async def verify(self, digest: bytes, blob: bytes,
        *args, **kwargs) -> bytes:
        """Verifies that `digest` is a valid signature with this public
        key on `blob`.
        """
        raise NotImplementedError
