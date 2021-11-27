"""Declares :class:`Keychain`."""
from .abstractkeystore import AbstractKeystore


class Keychain(AbstractKeystore):
    """Provides an interface to lookup private keys for encryption and/or
    signing.
    """
    __module__ = 'unimatrix.ext.crypto'


chain = Keychain()
