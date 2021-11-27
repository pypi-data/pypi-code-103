# pylint: skip-file
import os
import unittest

from ..algorithms import HMACSHA224
from ..algorithms import HMACSHA256
from ..algorithms import HMACSHA384
from ..algorithms import HMACSHA512
from ..secret import SecretKey
from .base import SigningTestCase


class HMACSHA224TestCase(SigningTestCase):
    __test__ = True
    algorithm = HMACSHA224

    def get_private_key(self):
        return SecretKey({'secret': 'foo'})


class HMACSHA256TestCase(HMACSHA224TestCase):
    algorithm = HMACSHA256


class HMACSHA384TestCase(HMACSHA224TestCase):
    algorithm = HMACSHA384


class HMACSHA512TestCase(HMACSHA224TestCase):
    algorithm = HMACSHA512
