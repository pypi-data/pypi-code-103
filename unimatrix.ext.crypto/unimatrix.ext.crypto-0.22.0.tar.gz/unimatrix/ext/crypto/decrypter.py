"""Declares :class:`Decrypter`."""
import abc


class Decrypter(metaclass=abc.ABCMeta):
    """Specifies the interface to decrypt ciphertext. It can also
    encrypt (since it possesses the private key).
    """

    def async_decrypt(self, buf):
        """Returns the plain text of byte-sequence `plain`."""
        raise NotImplementedError

    def async_encrypt(self, plain):
        """Returns the cipher text of byte-sequence `plain`."""
        raise NotImplementedError

    def encrypt(self, plain):
        """Returns the cipher text of byte-sequence `plain`."""
        raise NotImplementedError

    def decrypt(self, buf):
        """Returns the plain text of byte-sequence `plain`."""
        raise NotImplementedError
