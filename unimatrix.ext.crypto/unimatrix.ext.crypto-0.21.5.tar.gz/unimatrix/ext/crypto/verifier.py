"""Declares :class:`Verifier`."""
import abc

from cryptography.exceptions import InvalidSignature


class Verifier(metaclass=abc.ABCMeta):
    """Declares an interface to verify signatures."""

    @abc.abstractmethod
    def verify(self, signature):
        """Return a boolean indicating if `signature` is valid."""
        raise NotImplementedError


class LocalVerifier(Verifier):
    """A :class:`Verifier` implementation that uses a local
    public key.
    """

    @abc.abstractproperty
    def key(self):
        raise NotImplementedError

    def verify(self, sig: bytes, digest: bytes, *args, **kwargs) -> bytes:
        try:
            self.key.verify(bytes(sig), digest, *args, **kwargs)
            return True
        except InvalidSignature:
            return False
