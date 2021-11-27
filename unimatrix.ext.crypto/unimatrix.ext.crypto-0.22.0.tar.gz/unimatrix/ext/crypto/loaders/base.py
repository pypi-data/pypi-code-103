"""Declares :class:`BaseLoader`."""
from unimatrix.lib.datastructures import ImmutableDTO


class BaseLoader:
    """Declares the interface for all public key loaders."""
    __module__ = 'unimatrix.ext.crypto.loaders'

    @property
    def annotations(self) -> ImmutableDTO:
        return self.__annotations

    @property
    def opts(self) -> ImmutableDTO:
        return self.__opts

    @property
    def tags(self) -> set:
        return set(self.__tags)

    def __init__(self, opts, tags: set = None, annotations: dict = None):
        self.__opts = ImmutableDTO.fromdict(opts)
        self.__tags = set(tags or [])
        self.__annotations = ImmutableDTO.fromdict(annotations or {})
        self.setup(self.__opts)

    def annotate(self, key):
        """Applies the configured annotations to a key."""
        for annotation, value in dict.items(self.__annotations):
            key.annotate(annotation, value)

    def setup(self, opts):
        """Hook for implementations to initialize a new :class:`BaseLoader`
        instance.
        """
        pass

    async def import_keys(self):
        """Invokes :meth:`load` to retrieve :class:`TrustedPublicKey`
        instances and applies tags, annotations.
        """
        for key in await self.load():
            self.tag(key)
            self.annotate(key)
            yield key

    async def load(self):
        """Return an iterator that yields :class:`TrustedPublicKey`
        instances.
        """
        raise NotImplementedError

    def tag(self, key):
        """Applies the configured tags to a key."""
        for tag in self.__tags:
            key.tag(tag)
