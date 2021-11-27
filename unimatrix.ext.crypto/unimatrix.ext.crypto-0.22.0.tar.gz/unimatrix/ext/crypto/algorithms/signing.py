"""Declares :class:`SigningAlgorithm`."""
import abc

from cryptography.hazmat.primitives import hashes

from ..signature import Signature
from .base import Algorithm


class SigningAlgorithm(Algorithm):
    signature_class = Signature
    IncompatibleKey = type('IncompatibleKey', (Exception,), {})

    def digest(self, message):
        """Create a message digest using the configured hash algorithm."""
        assert hasattr(self, 'hashfunc') # nosec
        hasher = hashes.Hash(self.hashfunc())
        hasher.update(message)
        return hasher.finalize()

    async def sign(self, key, data: bytes) -> Signature:
        if not await key.can_use(self):
            raise self.IncompatibleKey
        digest = await key.sign(data, oid=self.oid, **self.get_sign_parameters(key))
        return self.signature_class(
            self.normalize_signature(digest), self, keyid=key.keyid
        )

    def verify(self, key, signature: bytes, digest: bytes) -> bool:
        return key.verify(signature, digest, **self.get_verify_parameters(key))

    @abc.abstractmethod
    def get_sign_parameters(self, key) -> dict:
        """Return a dictionary containing the parameters supplied to the
        :meth:`~unimatrix.ext.crypto.PrivateKey.sign()` method.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def get_verify_parameters(self, key) -> dict:
        """Return a dictionary containing the parameters supplied to the
        :meth:`~unimatrix.ext.crypto.PrivateKey.verify()` method.
        """
        raise NotImplementedError

    def normalize_signature(self, sig):
        """Normalize the signature, if necessary."""
        return sig

    def __hash__(self):
       raise NotImplementedError
