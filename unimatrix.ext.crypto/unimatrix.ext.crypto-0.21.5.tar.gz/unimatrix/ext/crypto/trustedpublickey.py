"""Declares :class:`TrustedPublicKey`."""
from .parsing import parse_jwk
from .verifier import LocalVerifier


class TrustedPublicKey(LocalVerifier):
    """Represents a public key that is trusted by a
    software application.
    """
    __module__ = 'unimatrix.ext.crypto'
    alias = name = None

    @property
    def keyid(self) -> str:
        return self.__public.keyid

    @property
    def key(self):
        return self.__public

    @classmethod
    def fromjwk(cls, jwk):
        key = cls(parse_jwk(jwk))
        if jwk.get('use') == 'sig':
            key.allow_usage('sign')
        return key

    def __init__(self, public):
        self.__public = public
        self.__usage = set()
        self.__tags = set()
        self.__annotations = dict()

    def allow_usage(self, operation):
        """Allow use of the key for the given `operation`. Must be ``'sign'``
        or ``'encrypt'``.
        """
        if operation not in ('sign', 'encrypt'):
            raise ValueError(operation)
        self.__usage.add(operation)

    def annotate(self, key, value):
        """Annotate the :class:`TrustedPublicKey` with the
        given `value` for `key`.
        """
        self.__annotations[key] = value

    def can_verify(self) -> bool:
        """Return a boolean indicating if the key may be used for signature
        verification.
        """
        return 'sign' in self.__usage

    def get_annotation(self, annotation, namespace: str = None) -> str:
        """Return the given `annotation`."""
        if namespace is not None:
            annotation = f'{namespace}/{annotation}'
        return self.__annotations[annotation]

    def is_annotated(self, annotation, namespace: str = None):
        """Return a boolean if the key is annotated with the
        given `annotation`.
        """
        if namespace is not None:
            annotation = f'{namespace}/{annotation}'
        return annotation in self.__annotations

    def is_tagged(self, tag: str) -> bool:
        """Return a boolean indicating if the key has the
        given `tag`.
        """
        return tag in self.__tags

    def tag(self, value: str):
        self.__tags.add(value)

    def __hash__(self):
        return hash(self.keyid)
