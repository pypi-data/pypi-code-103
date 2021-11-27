# pylint: skip-file
import asyncio
import time
import unittest

from fastapi.testclient import TestClient
from ioc.exc import UnsatisfiedDependency

from .. import ResourceEndpointSet
from .. import __unimatrix__ as boot
from ..asgi import Application


class BearerAuthorizationTestCase(unittest.TestCase):

    class view_class(ResourceEndpointSet):
        trust_local = True

        async def create(self):
            pass

        async def index(self):
            pass

        async def retrieve(self, resource_id):
            pass

    def setUp(self):
        asyncio.run(boot.on_setup())
        self.app = Application(
            allowed_hosts=['*'],
            enable_debug_endpoints=True
        )
        self.client = TestClient(self.app)
        self.view_class.add_to_router(self.app, '/test')

    def get_token(self, claims: dict = None):
        now = int(time.time())
        claims = claims or {}
        claims.setdefault('iss', 'self')
        claims.setdefault('aud', 'self')
        claims.setdefault('sub', 'self')
        claims.setdefault('iat', now)
        claims.setdefault('exp', now+60)
        response = self.client.post('/debug/token', json=claims or {})
        return response.text

    def test_retrieve_malformed(self):
        headers = {'Authorization': f'Bearer not-a-jwt'}
        response = self.client.get('/test/1', headers=headers)
        self.assertEqual(response.status_code, 403, response.text)

    def test_retrieve_unauthenticated(self):
        response = self.client.get('/test/1')
        self.assertEqual(response.status_code, 401, response.text)

    def test_retrieve_authenticated(self):
        headers = {'Authorization': f'Bearer {self.get_token()}'}
        response = self.client.get('/test/1', headers=headers)
        self.assertEqual(response.status_code, 200, response.text)

    def test_retrieve_expired(self):
        token = self.get_token({'exp': 1})
        headers = {'Authorization': f'Bearer {token}'}
        response = self.client.get('/test/1', headers=headers)
        dto = response.json()
        self.assertEqual(response.status_code, 403, response.text)
        self.assertIn('code', dto)
        self.assertEqual(dto['code'], 'CREDENTIAL_EXPIRED')

    def test_create_unauthenticated(self):
        response = self.client.post('/test')
        self.assertEqual(response.status_code, 401, response.text)

    def test_create_authenticated(self):
        headers = {'Authorization': f'Bearer {self.get_token()}'}
        response = self.client.post('/test', headers=headers)
        self.assertEqual(response.status_code, 200, response.text)

    def test_create_expired(self):
        token = self.get_token({'exp': 1})
        headers = {'Authorization': f'Bearer {token}'}
        response = self.client.post('/test', headers=headers)
        dto = response.json()
        self.assertEqual(response.status_code, 403, response.text)
        self.assertIn('code', dto)
        self.assertEqual(dto['code'], 'CREDENTIAL_EXPIRED')

    def test_index_unauthenticated(self):
        response = self.client.get('/test')
        self.assertEqual(response.status_code, 401, response.text)

    def test_index_authenticated(self):
        headers = {'Authorization': f'Bearer {self.get_token()}'}
        response = self.client.get('/test', headers=headers)
        self.assertEqual(response.status_code, 200, response.text)

    def test_index_expired(self):
        token = self.get_token({'exp': 1})
        headers = {'Authorization': f'Bearer {token}'}
        response = self.client.get('/test', headers=headers)
        dto = response.json()
        self.assertEqual(response.status_code, 403, response.text)
        self.assertIn('code', dto)
        self.assertEqual(dto['code'], 'CREDENTIAL_EXPIRED')


class IssuerAuthenticationTestCase(BearerAuthorizationTestCase):
    issuer = "foo"

    def get_token(self, claims: dict = None):
        return super().get_token({"iss": self.issuer, **(claims or {})})

    class view_class(ResourceEndpointSet):
        trust_local = True
        trusted_issuers = ["foo"]

        async def create(self):
            pass

        async def index(self):
            pass

        async def retrieve(self, resource_id):
            pass

    def test_invalid_issuer_is_rejected(self):
        token = self.get_token({'iss': "bar"})
        headers = {'Authorization': f'Bearer {token}'}
        response = self.client.post('/test', headers=headers)
        self.assertEqual(response.status_code, 403, response.text)


class AudienceAuthenticationTestCase(BearerAuthorizationTestCase):
    issuer = "foo"

    def get_token(self, claims: dict = None):
        return super().get_token({"aud": self.issuer, **(claims or {})})

    class view_class(ResourceEndpointSet):
        trust_local = True
        accepted_audiences = ["foo"]

        async def create(self):
            pass

        async def index(self):
            pass

        async def retrieve(self, resource_id):
            pass

    def test_invalid_audience_is_rejected(self):
        token = self.get_token({'aud': "bar"})
        headers = {'Authorization': f'Bearer {token}'}
        response = self.client.post('/test', headers=headers)
        self.assertEqual(response.status_code, 403, response.text)


class ScopedAuthenticationTestCase(BearerAuthorizationTestCase):
    required_scope = ["foo", "bar", "baz"]

    def get_token(self, claims: dict = None):
        return super().get_token({
            "scope": str.join(" ", self.required_scope), **(claims or {})
        })

    class view_class(ResourceEndpointSet):
        trust_local = True
        required_scope = ["foo", "bar", "baz"]

        async def create(self):
            pass

        async def index(self):
            pass

        async def retrieve(self, resource_id):
            pass

    def test_insuffient_scope_is_rejected(self):
        token = self.get_token({'scope': "foo bar"})
        headers = {'Authorization': f'Bearer {token}'}
        response = self.client.post('/test', headers=headers)
        self.assertEqual(response.status_code, 401, response.text)

    def test_extra_scope_is_acccepted(self):
        token = self.get_token({'scope': "foo bar baz taz"})
        headers = {'Authorization': f'Bearer {token}'}
        response = self.client.post('/test', headers=headers)
        self.assertEqual(response.status_code, 200, response.text)


class DefaultPolicyIsRejectTestCase(unittest.TestCase):

    def get_token(self, claims: dict = None):
        response = self.client.post('/debug/token', json=claims or {})
        return response.text

    def setUp(self):
        asyncio.run(boot.on_setup())
        self.app = Application(
            allowed_hosts=['*'],
            enable_debug_endpoints=True
        )
        self.client = TestClient(self.app)
        self.view_class.add_to_router(self.app, '/test')

    class view_class(ResourceEndpointSet):

        async def create(self):
            pass

    def test_no_policy_rejects_all(self):
        token = self.get_token()
        headers = {'Authorization': f'Bearer {token}'}
        response = self.client.post('/test', headers=headers)
        self.assertEqual(response.status_code, 403, response.text)
