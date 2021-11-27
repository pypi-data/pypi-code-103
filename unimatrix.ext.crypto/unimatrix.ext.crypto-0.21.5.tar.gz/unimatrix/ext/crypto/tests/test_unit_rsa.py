# pylint: skip-file
import os

from ..algorithms import RSAPKCS1v15SHA256
from ..algorithms import RSAPKCS1v15SHA384
from ..algorithms import RSAPKCS1v15SHA512
from ..algorithms import RSAOAEPSHA256
from ..pkcs import RSAPrivateKey
from .base import EncryptionTestCase
from .base import SigningTestCase


PRIVATE_KEY = os.path.join(os.path.dirname(__file__), 'key.rsa')


class RSAPKCS1v15SHA256TestCase(SigningTestCase):
    __test__ = True
    algorithm = RSAPKCS1v15SHA256

    def get_data(self, *args, **kwargs):
        return self.algorithm.digest(super().get_data(*args, **kwargs))

    def get_private_key(self):
        return RSAPrivateKey({'path': PRIVATE_KEY})


class RSAPKCS1v15SHA384TestCase(RSAPKCS1v15SHA256TestCase):
    algorithm = RSAPKCS1v15SHA384


class RSAPKCS1v15SHA512TestCase(RSAPKCS1v15SHA256TestCase):
    algorithm = RSAPKCS1v15SHA512


class RSAOAEPSHA256TestCase(EncryptionTestCase):
    __test__ = True
    algorithm = RSAOAEPSHA256

    def get_private_key(self):
        return RSAPrivateKey({'path': PRIVATE_KEY})
