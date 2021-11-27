"""Declares :class:`Signer`."""
import abc

from .algorithms import Algorithm
from .algorithms import HMACSHA256
from .algorithms import HMACSHA384
from .algorithms import HMACSHA512
from .private import PrivateKey
from .public import PublicKey
from .signature import Signature


class Signer(metaclass=abc.ABCMeta):
    """Declares the mandatory interface for all :class:`Signer`
    implementations.
    """
    __module__ = 'unimatrix.ext.crypto'
    signature_class = Signature
    public_key: PublicKey = None

    class wrapper_class:

        def __init__(self, algorithm, key):
            self.algorithm = algorithm
            self.key = key

        def verify(self, signature, digest):
            return self.algorithm.verify(self.key, signature, digest)

    async def sign(self, message: bytes, algorithm=None) -> Signature:
        """Signs byte-sequence `message` and returns the corresponding signature.

        Args:
            message (bytes): the data to be signed.
            algorithm: an instruction for the signer on the algorithm to use.

        Returns:
            :class:`~unimatrix.ext.crypto.Signature`
        """
        signature = await (algorithm or self.algorithm).sign(self.key, message)

        # TODO: why is this here?
        if self.public_key is None:
            self.public_key = self.wrapper_class(
                self.algorithm,
                self.get_public_key()
            )
        return signature

    def algorithm(self) -> Algorithm:
        """Return the algorithm used by the signer."""
        raise NotImplementedError

    def digest(self, message):
        """Create a message digest using the configured hash algorithm."""
        return self.algorithm.digest(message)

    def get_public_key(self):
        """Return the public key used by the signer."""
        raise NotImplementedError


class ApplicationSigner(Signer):
    """A :class:`Signer` implementation that is configured with the
    :term:`Application Secret Key`.
    """
    _symbolic_mapping = {
        'sha256': HMACSHA256,
        'sha384': HMACSHA384,
        'sha512': HMACSHA512,
    }

    @property
    def algorithm(self) -> str:
        """Return the algorithm used by the signer."""
        alg = getattr(self.key, 'default_algorithm', 'sha256')
        return self._symbolic_mapping[alg]

    def __init__(self, key):
        self.key = key

    def get_public_key(self):
        """Return the public key used by the signer."""
        return self.key


class GenericSigner(Signer):
    """A :class:`Signer` implementation that is configured by passing a key
    and an algorithm to its constructor.

    Example:

    .. code:: python

        from unimatrix.ext import crypto

        signer = crypto.GenericSigner(
            algorithm=crypto.algorithms.HMACSHA256,
            key=crypto.SecretKey({'secret': "my very secret key"})
        )
    """

    def __init__(self, algorithm: Algorithm, key: PrivateKey):
        self.algorithm = algorithm
        self.key = key
        self.public_key = None

    def get_public_key(self):
        return self.key.get_public_key()
