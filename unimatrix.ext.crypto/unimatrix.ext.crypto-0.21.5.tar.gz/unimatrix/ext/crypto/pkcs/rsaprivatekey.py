# pylint: disable=line-too-long
"""Declares :class:`RSAPrivateKey`."""
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.asymmetric import utils
from cryptography.hazmat.primitives.serialization import load_pem_private_key
from cryptography.exceptions import InvalidSignature

from ..private import PrivateKey
from .base import PKCSObject
from .pempublickey import RSAPublicKey


class RSAPrivateKey(PKCSObject, PrivateKey):
    """Uses an RSA private key to perform cryptographic operations.

    The options format recognized by this implementation is specified below:

    .. code:: python

        {
            "path": "/path/to/private/key",
            "content": b'-----BEGIN RSA PRIVATE KEY-----...'
        }
    """

    @property
    def id(self):
        return self.keyid

    @property
    def keyid(self):
        return self.get_public_key().keyid

    @classmethod
    def generate(cls, bits=2048):
        key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=bits
        )
        return cls({'key': key})

    def setup(self, opts):
        """Configures the :class:`RSAPrivateKey` using the given options `opts`.
        This method is called in the constructor and should not be called more
        than once.
        """
        if not bool(opts.get('content'))\
        ^ bool(opts.get('path'))\
        ^ bool(opts.get('key')):
            raise ValueError("Specify either .content or .path")
        content = opts.get('content')
        self._key = key = opts.get('key')
        if key is None:
            if opts.get('path'):
                content = open(opts.path, 'rb').read()
            self._key = load_pem_private_key(content, opts.get('password'))
        self._public = self._key.public_key()

    def has_public_key(self):
        """Return a boolean indicating if the private key is able to
        extract and provide its public key.
        """
        return True

    def get_public_key(self):
        return RSAPublicKey(self._public)

    async def decrypt(self, ct, padding):
        return self._key.decrypt(bytes(ct), padding)

    async def sign(self, blob: bytes, padding, algorithm, prehashed=True, *args, **kwargs) -> bytes:
        if not prehashed:
            raise NotImplementedError
        algorithm = utils.Prehashed(algorithm)
        return self._key.sign(blob, padding, algorithm)

    async def encrypt(self, pt, padding):
        return self._public.encrypt(bytes(pt), padding)

    def verify(self, digest: bytes, blob: bytes,
        padding, algorithm) -> bytes:
        try:
            self._public.verify(bytes(digest), blob, padding, algorithm)
            return True
        except InvalidSignature:
            return False
