"""Declares :class:`Signable`."""
import abc

from .signer import Signer
from .signature import Signature


class Signable(metaclass=abc.ABCMeta):
    """Specifies the basic interface for signable objects."""
    __module__ = 'unimatrix.ext.crypto'
    signature: Signature = None

    @abc.abstractmethod
    def get_signable_bytes(self, signer: Signer) -> bytes:
        """Return a byte-sequence holding the data that needs to be signed
        for the :class:`Signable`.
        """
        raise NotImplementedError

    async def sign(self, signer: Signer) -> Signature:
        """Use `signer` to create a signature and return an instance (of a
        subclass of) :class:`Signature`
        """
        if self.signature is None:
            self.signature = await signer.sign(self.get_signable_bytes(signer))
        return self.signature
