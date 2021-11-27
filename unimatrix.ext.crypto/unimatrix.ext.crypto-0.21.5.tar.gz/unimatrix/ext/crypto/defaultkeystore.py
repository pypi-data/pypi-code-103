"""Declares :class:`DefaultKeystore`."""
import copy

import ioc.loader
from unimatrix.conf import settings

from .abstractkeystore import AbstractKeystore


class DefaultKeystore(AbstractKeystore):
    """A :class:`AbstractKeystore` implementation that uses the application
    settings to select a key from a mapping, based on the key identifier.

    An example configuration is provided below:

    .. code:: python

        CRYPTO_KEYSTORE = {
            "some-random-id-1": {
                "backend": "unimatrix.ext.crypto.backends.google.AsymmetricKey",
                "options": {
                    'project': "myproject",
                    'location': "europe-west4",
                    'keyring': "mykeyring",
                    'key': "mykey",
                    'version': 1
                }
            }
        }
    """
    __module__ = 'unimatrix.ext.crypto'

    def __init__(self, initial=None):
        self.__keys = ...
        if initial is not None:
            self._load_keys(initial)

    def _load_keys(self, keystore=None):
        keys = keystore or getattr(settings, 'CRYPTO_KEYSTORE', {})
        self.__keys = {}
        for kid, config in dict.items(copy.deepcopy(keys)):
            Key = ioc.loader.import_symbol(config['class'])
            self.__keys[kid] = Key(
                config['options'],
                keyid=config.get('keyid') or kid
            )
            if config.get('keyid'):
                self.__keys[ config['keyid'] ] = self.__keys[kid]

    async def get(self, keyid):
        """Lookup the key identified by `keyid`. If `keyid` is ``None``, return
        the :term:`Application Secret Key`.
        """
        if self.__keys == ...:
            self._load_keys()
        if keyid is None:
            return get_secret_key()

        return self.__keys[keyid]
