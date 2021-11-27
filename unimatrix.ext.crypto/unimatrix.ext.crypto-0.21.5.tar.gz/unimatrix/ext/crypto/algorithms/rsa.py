# pylint: skip-file
import hashlib

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import utils
from cryptography.hazmat.primitives.asymmetric import padding

from .. import oid
from .encryption import EncryptionAlgorithm
from .signing import SigningAlgorithm


__all__ = [
    'RSAPKCS1v15SHA256',
    'RSAPKCS1v15SHA384',
    'RSAPKCS1v15SHA512',
    'RSAOAEPSHA256',
]


class RSAOAEP(EncryptionAlgorithm):
    __module__ = 'unimatrix.ext.crypto.algorithms'

    def __init__(self, oid, hashfunc):
        self.oid = oid
        self.hashfunc = hashfunc

    def get_encrypt_parameters(self, key, pt):
        return {
            'padding': padding.OAEP(
                mgf=padding.MGF1(algorithm=self.hashfunc()),
                algorithm=self.hashfunc(),
                label=None
            )
        }

    def get_decrypt_parameters(self, key, ct):
        return self.get_encrypt_parameters(key, None)

    def __hash__(self):
        return hash(f'rsaoaep-{self.hashfunc.__name__}')


class RSAPKCS1v15(SigningAlgorithm):
    __module__ = 'unimatrix.ext.crypto.algorithms'

    def __init__(self, oid, hashfunc):
        self.oid = oid
        self.hashfunc = hashfunc

    def get_sign_parameters(self, key):
        return {'padding': padding.PKCS1v15(), 'algorithm': self.hashfunc()}

    def get_verify_parameters(self, key):
        return {'padding': padding.PKCS1v15(), 'algorithm': self.hashfunc()}

    def __hash__(self):
        return hash(f'pkcsv15-{self.hashfunc.__name__}')


RSAPKCS1v15SHA256 = RSAPKCS1v15(oid.RSAPKCS1v15SHA256, hashes.SHA256)
RSAPKCS1v15SHA384 = RSAPKCS1v15(oid.RSAPKCS1v15SHA384, hashes.SHA384)
RSAPKCS1v15SHA512 = RSAPKCS1v15(oid.RSAPKCS1v15SHA512, hashes.SHA512)
RSAOAEPSHA256 = RSAOAEP(oid.RSAOAEP, hashes.SHA256)
