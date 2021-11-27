# pylint: disable=line-too-long
"""Declares :class:`AbstractKeystore`."""
from collections import OrderedDict

import ioc.loader
from unimatrix.lib.datastructures import ImmutableDTO

from .exceptions import UnsupportedBackend


class AbstractKeystore:
    """The base class for all :term:`Key Store` implementations. A Key Store
    provides an interface to lookup private or public keys.
    """

    @property
    def keys(self):
        return self.__keys

    @property
    def masked(self):
        return self.__masked

    def __init__(self):
        self.__keys = OrderedDict()
        self.__masked = OrderedDict()

    def clear(self):
        """Remove all keys from the key store."""
        self.__keys = {}
        self.__masked = {}

    def get(self, keyid):
        key = self.keys.get(keyid) or self.masked.get(keyid)
        if key is None:
            raise LookupError
        return key

    def register(self, key, force=False):
        if key.keyid in self.masked and not force:
            raise ValueError(f"Key already registered: {key.keyid}")
        self.masked[key.keyid] = key
        if key.alias or key.name:
            self.keys[key.alias or key.name] = key

    def register_deferred(self, config):
        self.register(Key.new(self, **config))

    def __iter__(self):
        return iter(self.keys.values())

    def __contains__(self, name):
        return name in {**self.keys, **self.masked}\
            or name in dict.values(self.masked)

    def __getitem__(self, k):
        return list(self.__masked.values())[k]


class Key:
    __loaders = {
        'azure': 'unimatrix.ext.crypto.backends.azure.AzureBackend',
        'google': 'unimatrix.ext.crypto.backends.GoogleCloudKMSLoader',
        'pem:disk': 'unimatrix.ext.crypto.backends.disk.LocalDiskBackend',
        'urn:unimatrix:cloud:azure': 'unimatrix.ext.crypto.backends.azure.AzureBackend',
        'urn:unimatrix:cloud:google': 'unimatrix.ext.crypto.backends.GoogleCloudKMSLoader'
    }

    @property
    def name(self):
        return self.__name

    @property
    def alias(self):
        return self.__alias

    @property
    def id(self):
        return self.keyid

    @property
    def keyid(self):
        return self.__key.keyid

    @classmethod
    def new(cls, chain, **config):
        key = cls(chain, **config)
        key.load()
        return key

    def __init__(self, chain, name, usage, loader, alias=None):
        self.__chain = chain
        self.__name = name
        self.__usage = usage
        self.__loader_class, self.__loader__opts = self.__get_loader(**loader)
        self.__key = None
        self.__alias = alias

    def __get_loader(self, backend, opts):
        if backend not in self.__loaders:
            raise UnsupportedBackend(backend)
        return (
            ioc.loader.import_symbol(self.__loaders[backend]),
            ImmutableDTO.fromdict(opts)
        )

    async def can_use(self, *args, **kwargs):
        return await self.__key.can_use(*args, **kwargs)

    def get_public_key(self, *args, **kwargs):
        return self.__key.get_public_key(*args, **kwargs)

    async def sign(self, *args, **kwargs):
        return await self.__key.sign(*args, **kwargs)

    def load(self):
        """Loads the actual key from the backend."""
        backend = self.__loader_class(self.__loader__opts)
        self.__key = backend.get_sync(self.__name)

    def verify(self, *args, **kwargs):
        return self.__key.public.verify(*args, **kwargs)
