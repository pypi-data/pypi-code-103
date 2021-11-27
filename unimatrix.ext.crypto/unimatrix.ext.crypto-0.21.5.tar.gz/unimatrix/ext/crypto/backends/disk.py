"""Declares :class:`LocalDiskBackend`."""
import os

from cryptography.hazmat.primitives.asymmetric import utils
from cryptography.hazmat.primitives.asymmetric.ec import EllipticCurvePrivateNumbers
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPrivateNumbers
from cryptography.hazmat.primitives.serialization import load_pem_private_key

from .. import algorithms
from ..ec import EllipticCurvePublicKey
from ..pkcs import RSAPublicKey
from ..keyloader import KeyLoader


class LocalDiskBackend(KeyLoader):
    algorithms = {
        EllipticCurvePrivateNumbers: [
            algorithms.SECP256K1SHA256,
            algorithms.SECP256R1SHA256,
        ],
        RSAPrivateNumbers: [
            algorithms.RSAPKCS1v15SHA256,
            algorithms.RSAPKCS1v15SHA384,
            algorithms.RSAPKCS1v15SHA512,
            algorithms.RSAOAEPSHA256
        ]
    }

    async def sign(self, wrapper, digest, algorithm, padding, *args, **kwargs):
        return wrapper.private.sign(
            data=digest,
            padding=padding,
            algorithm=utils.Prehashed(algorithm)
        )

    def setup(self, opts):
        self.workdir = opts.dirname

    def get_algorithms(self, dto):
        if hasattr(dto, 'private_numbers'):
            cls = type(dto.private_numbers())
            return self.algorithms[cls]
        else:
            raise NotImplementedError

    def get_private_key(self, dto):
        return dto

    def get_public_key(self, client, dto):
        numbers = dto.private_numbers()
        if isinstance(numbers, EllipticCurvePrivateNumbers):
            return EllipticCurvePublicKey(dto.public_key())
        elif isinstance(numbers, RSAPrivateNumbers):
            return RSAPublicKey(dto.public_key())
        else:
            raise NotImplementedError(dto)

    def get_qualname(self, dto):
        return ''

    def get_sync(self, name):
        with open(os.path.join(self.workdir, name), 'rb') as f:
            return self.key_factory(
                None, name, load_pem_private_key(f.read(), None))

    def get_version(self, dto):
        return None

