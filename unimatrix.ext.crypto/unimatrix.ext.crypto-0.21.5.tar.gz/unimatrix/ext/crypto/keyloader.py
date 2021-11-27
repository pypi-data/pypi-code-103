"""Declares :class:`KeyLoader`."""
import abc
import logging

from unimatrix.lib.datastructures import ImmutableDTO

from .keychain import chain as default_chain
from .truststore import trust as default_trust


class KeyLoader(metaclass=abc.ABCMeta):
    """Declares the interface for all Key Loader implementations. A
    key loader knows how to retrieve keys from various backends. For
    the reference example, see the :mod:`unimatrix.ext.crypto.google`
    module.
    """
    logger = logging.getLogger('unimatrix.ext.crypto')
    default_timeout = 5.0

    #: Maps known algorithm names to platform-specific
    #: names.
    supported_algorithms: dict = {}

    def __init__(self, opts, public_only=False):
        self.__opts = opts
        self.__public_only = public_only
        self.setup(ImmutableDTO.fromdict(opts))

    def setup(self, opts):
        """Hook called during instance initialization."""
        pass

    @abc.abstractmethod
    def get_algorithms(self, dto) -> set:
        """Return the supported algorithms given a key object returned
        from the client.
        """
        raise NotImplementedError

    def get_platform_algorithm_name(self, oid):
        """Lookup the platform identifier for a specific signing
        or encryption algorithm, by oid.
        """
        return self.supported_algorithms[oid]

    @abc.abstractmethod
    def get_public_key(self, dto) -> str:
        """Return the public key given a key object returned
        from the client.
        """
        raise NotImplementedError

    def get_private_key(self, dto):
        """Returns the private key for local disk algorithms."""
        return None

    @abc.abstractmethod
    def get_qualname(self, dto) -> str:
        """Return the qualified name given a key object returned
        from the client.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def get_version(self, dto) -> str:
        """Return the version given a key object returned
        from the client.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def get_sync(self, name, *args, **kwargs):
        """Return the key identified by name. If the cryptographic
        backend maintains multiple key *versions*, return
        the latest version of the key.
        """
        raise NotImplementedError

    async def load(self, chain=None, trust=None):
        """Load all keys and add them to the :term:`Key Store` and
        :term:`Trust Store`.
        """
        chain = chain or default_chain
        trust = trust or default_trust
        async for key in self.list():
            if key.is_private():
                if not self.__public_only:
                    chain.register(key.id, key)
                if key.has_public_key():
                    trust.register(key.id, await key.get_public_key())
                continue
            if key.is_public():
                trust.register(key.id, key)
                continue

    def key_factory(self, client, name, dto):
        return self.key_class(self, self.get_qualname(dto), name,
            self.get_version(dto), self.get_algorithms(dto),
            public=self.get_public_key(client, dto),
            private=self.get_private_key(dto))

    class key_class:

        @property
        def keyid(self):
            if self.public is None:
                raise NotImplementedError
            return self.public.keyid

        def __init__(self, backend, qualname, name, version, algorithms, public=None, private=None):
            self.backend = backend
            self.qualname = qualname
            self.name = name
            self.version = version
            self.algorithms = algorithms
            self.public = public
            self.private = private

        async def can_use(self, algorithm):
            return algorithm in self.algorithms

        async def sign(self, *args, **kwargs):
            """Invoke :attr:`backend` to sign a message digest."""
            return await self.backend.sign(self, *args, **kwargs)

        def verify(self, sig, digest, *args, **kwargs):
            return self.public.verify(sig, digest, *args, **kwargs)

        def get_public_key(self):
            """Returns the public key for asymmetric algorithms."""
            return self.public
