"""Declares :class:`PrivateKey`."""
import abc
import warnings

from cryptography.hazmat.primitives import serialization

from unimatrix.lib.datastructures import ImmutableDTO
from .algorithms.base import Algorithm


class PrivateKey(metaclass=abc.ABCMeta):
    """Provides an interface for signing and decryption
    operations.
    """
    __module__ = 'unimatrix.ext.crypto'
    capabilities = abc.abstractproperty()

    @property
    def id(self):
        """Return the identifier of the key."""
        return self.__keyid

    @property
    def keyid(self):
        """Return the identifier of the key."""
        return self.__keyid

    @property
    def metadata(self):
        return ImmutableDTO.fromdict(
            {**self.get_metadata(), 'keyid': self.__keyid})

    @property
    def opts(self) -> ImmutableDTO:
        """Returns the options that were used to configure the key."""
        return self.__opts

    @property
    def pem(self) -> bytes:
        """Return a byte-sequence holding the PEM-encoded key,
        if supported.
        """
        return self._key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )

    @classmethod
    def generate(cls, bits=2048):
        raise NotImplementedError

    def __init__(self, opts, keyid=None):
        self.__keyid = keyid
        self.__opts = ImmutableDTO(opts)
        self.setup(self.__opts)

    @abc.abstractmethod
    def setup(self, opts):
        raise NotImplementedError

    def get_metadata(self) -> dict:
        return {}

    def has_public_key(self):
        """Return a boolean indicating if the private key is able to
        extract and provide its public key.
        """
        raise NotImplementedError

    def is_private(self) -> bool:
        """Return a boolean indicating if the key is private."""
        return True

    def is_public(self) -> bool:
        """Return a boolean indicating if the key is public."""
        return False

    async def can_use(self, alg: Algorithm) -> bool:
        """Return a boolean if the key can use the algorithm identified by
        the provided `oid`.
        """
        return alg in self.capabilities

    async def encrypt(self, blob: bytes, *args, **kwargs) -> bytes:
        """Returns the cipher text of byte-sequence `blob`."""
        raise NotImplementedError

    async def decrypt(self, blob: bytes, *args, **kwargs) -> bytes:
        """Returns the plain text of byte-sequence `blob`."""
        raise NotImplementedError

    def get_public_key(self):
        """Return the public key."""
        raise NotImplementedError

    async def sign(self, blob: bytes, *args, **kwargs) -> bytes:
        """Returns the digest of byte-sequence `blob`."""
        raise NotImplementedError

    def verify(self, digest: bytes, blob: bytes,
        *args, **kwargs) -> bytes:
        """Verifies that `digest` is valid for `blob`."""
        raise NotImplementedError
