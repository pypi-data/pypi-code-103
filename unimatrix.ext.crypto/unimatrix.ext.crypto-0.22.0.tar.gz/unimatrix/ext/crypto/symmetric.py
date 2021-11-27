"""Declares :class:`BaseSymmetricKey`."""
import abc


class BaseSymmetricKey(metaclass=abc.ABCMeta):
    """The base class for all symmetric encryption implementations."""
    capabilities = []

    @abc.abstractmethod
    def encrypt(self, buf):
        """Returns the cipher text of byte-sequence `buf`."""
        raise NotImplementedError

    @abc.abstractmethod
    def decrypt(self, buf):
        """Returns the plain text of byte-sequence `buf`."""
        raise NotImplementedError

    async def async_encrypt(self, blob):
        """Asynchronously encrypt byte-sequence `blob` using the underlying
        encryption backend.
        """
        raise NotImplementedError

    async def async_decrypt(self, blob):
        """Asynchronously decrypt byte-sequence `blob` using the underlying
        decryption backend.
        """
        raise NotImplementedError

    def has_capability(self, cap):
        """Return a boolean indicating if the key has the given capability
        `cap`.
        """
        return cap in self.capabilities
