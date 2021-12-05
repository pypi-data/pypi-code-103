# pylint: skip-file
import asyncio
import time
import unittest

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.serialization import Encoding
from cryptography.hazmat.primitives.serialization import PrivateFormat
from cryptography.hazmat.primitives.serialization import NoEncryption
from fastapi.testclient import TestClient
from unimatrix.ext import crypto
from unimatrix.ext import jose
from unimatrix.ext.crypto.pkcs import RSAPrivateKey
from unimatrix.ext.crypto.ec import EllipticCurvePrivateKey
from unimatrix.ext.crypto.trustedpublickey import TrustedPublicKey
from unimatrix.lib.datastructures import DTO

from .. import ResourceEndpointSet
from .. import __unimatrix__ as boot
from ..asgi import Application
from ..keytrustpolicy import KeyTrustPolicy


class ECKeyTrustTestCase(unittest.TestCase):
    issuer = "self"
    curve = ec.SECP256K1

    class view_class(ResourceEndpointSet):
        trust_policy = KeyTrustPolicy(['foo'])

        async def create(self):
            pass

        async def index(self):
            pass

        async def retrieve(self, resource_id):
            pass

    def generate_key(self):
        return EllipticCurvePrivateKey.generate('P-256')

    def get_signer(self, key):
        return crypto.GenericSigner(crypto.SECP256R1SHA256, key)

    def setUp(self):
        # k1: trusted and accepted by policy; k2 trusted but rejected by
        # policy; k3 not trusted; k4 matches a different policy
        self.k1 = self.generate_key()
        self.k2 = self.generate_key()
        self.k3 = self.generate_key()
        self.k4 = self.generate_key()

        self.s1 = self.get_signer(self.k1)
        self.s2 = self.get_signer(self.k2)
        self.s3 = self.get_signer(self.k3)
        self.s4 = self.get_signer(self.k4)

        now = int(time.time())
        claims = {
            'iss': self.issuer,
            'aud': 'self',
            'iat': now,
            'exp': now + 300,
            'sub': "foo"
        }
        self.t1 = jose.jwt.sync(claims, signer=self.s1)
        self.t2 = jose.jwt.sync(claims, signer=self.s2)
        self.t3 = jose.jwt.sync(claims, signer=self.s3)
        self.t4 = jose.jwt.sync(claims, signer=self.s4)

        # Verify that the signatures are valid.
        asyncio.run(  jose.parse(bytes(self.t1)).verify(self.k1.get_public_key()) )
        asyncio.run(  jose.parse(bytes(self.t2)).verify(self.k2.get_public_key()) )
        asyncio.run(  jose.parse(bytes(self.t3)).verify(self.k3.get_public_key()) )
        asyncio.run(  jose.parse(bytes(self.t4)).verify(self.k4.get_public_key()) )

        # Run this before adding the public key
        asyncio.run(boot.on_setup())

        # Add the key to the trusted key store.
        self.p1 = TrustedPublicKey(self.k1.get_public_key())
        self.p4 = TrustedPublicKey(self.k4.get_public_key())
        self.p1.tag('foo')
        self.p4.tag('bar')
        crypto.trust.register(self.p1)
        crypto.trust.register(self.p4)
        crypto.trust.register(TrustedPublicKey(self.k2.get_public_key()))

        self.app = Application(
            allowed_hosts=['*'],
            enable_debug_endpoints=True
        )
        self.client = TestClient(self.app)
        self.view_class.add_to_router(self.app, '/test')

    def tearDown(self):
        crypto.trust.clear()

    def test_policy_match_is_accepted(self):
        headers = {'Authorization': f'Bearer {self.t1}'}
        response = self.client.get('/test/1', headers=headers)
        self.assertEqual(response.status_code, 200, response.text)

    def test_no_policy_match_is_rejected(self):
        headers = {'Authorization': f'Bearer {self.t2}'}
        response = self.client.get('/test/1', headers=headers)
        self.assertEqual(response.status_code, 403, response.text)

    def test_untrusted_is_rejected(self):
        headers = {'Authorization': f'Bearer {self.t3}'}
        response = self.client.get('/test/1', headers=headers)
        self.assertEqual(response.status_code, 403, response.text)

    def test_other_policy_trusted_is_rejected(self):
        headers = {'Authorization': f'Bearer {self.t4}'}
        response = self.client.get('/test/1', headers=headers)
        self.assertEqual(response.status_code, 403, response.text)


class RSAKeyTrustTestCase(ECKeyTrustTestCase):

    def generate_key(self):
        private_key = rsa.generate_private_key(65537, 2048)\
            .private_bytes(
                encoding=Encoding.PEM,
                format=PrivateFormat.TraditionalOpenSSL,
                encryption_algorithm=NoEncryption()
            )
        return RSAPrivateKey(DTO(content=private_key))

    def get_signer(self, key):
        return crypto.GenericSigner(crypto.RSAPKCS1v15SHA256, key)
