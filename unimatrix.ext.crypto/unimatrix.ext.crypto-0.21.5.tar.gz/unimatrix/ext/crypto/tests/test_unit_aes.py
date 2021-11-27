# pylint: skip-file
import asyncio
import os
import unittest

from ..algorithms import AES256GCM
from ..secret import SecretKey
from .base import EncryptionTestCase


class AES256GCMTestCase(EncryptionTestCase):
    __test__ = True
    algorithm = AES256GCM

    def get_private_key(self):
        return SecretKey({'secret': b"Hello world!"})

