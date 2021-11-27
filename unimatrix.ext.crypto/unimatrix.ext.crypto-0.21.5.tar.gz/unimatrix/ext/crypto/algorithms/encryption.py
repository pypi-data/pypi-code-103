"""Declares :class:`EncryptionAlgorithm`."""
import abc

from unimatrix.lib.datastructures import ImmutableDTO

from ..plaintext import Plaintext
from ..ciphertext import Ciphertext
from .base import Algorithm


class EncryptionAlgorithm(Algorithm):
    ct_class = Ciphertext
    IncompatibleKey = type('IncompatibleKey', (Exception,), {})

    def pre_encrypt(self, key, pt):
        pass

    def post_encrypt(self, key, ct, *args, **kwargs):
        pass

    async def encrypt(self, key, pt: Plaintext, *args, **kwargs) -> Ciphertext:
        if not await key.can_use(self):
            raise self.IncompatibleKey
        if isinstance(pt, bytes):
            pt = Plaintext(pt)
        params = ImmutableDTO.fromdict(self.get_encrypt_parameters(key, pt))
        kwargs = {**params, **kwargs}
        self.pre_encrypt(key, pt)
        ct = self.ct_class(await key.encrypt(pt, *args, **kwargs), self)
        self.post_encrypt(key, pt, ct)
        return ct

    async def decrypt(self, key, ct: Ciphertext):
        if not await key.can_use(self):
            raise IncompatibleKey
        return await key.decrypt(ct, **self.get_decrypt_parameters(key, ct))

    @abc.abstractmethod
    def get_encrypt_parameters(self, key, pt) -> dict:
        raise NotImplementedError

    @abc.abstractmethod
    def get_decrypt_parameters(self, key, ct) -> dict:
        raise NotImplementedError


class AuthenticatedEncryptionAlgorithm(EncryptionAlgorithm):
    cipher_class = abc.abstractproperty()

    def post_encrypt(self, key, pt, ct):
        ct.nonce = pt.nonce
        ct.aad = pt.aad
