from unittest import TestCase
from unittest.mock import MagicMock, patch

from ai_api_client_sdk.exception import AIAPIAuthenticatorException
from ai_api_client_sdk.helpers.authenticator import Authenticator


class TestAuthenticator(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.auth_url = 'test_auth_url'
        cls.client_id = 'test_client_id'
        cls.client_secret = 'test_client_secret'

    @patch('ai_api_client_sdk.helpers.authenticator.requests')
    def test_authenticator(self, requests_mock):
        token = 'test_token'
        response_mock = MagicMock()
        response_mock.json.return_value = {'access_token': token}
        requests_mock.post.return_value = response_mock
        data = {'grant_type': 'client_credentials', 'client_id': self.client_id, 'client_secret': self.client_secret}
        a = Authenticator(auth_url=self.auth_url, client_id=self.client_id, client_secret=self.client_secret)
        generated_token = a.get_token()
        requests_mock.post.assert_called_with(url=self.auth_url, data=data)
        self.assertEqual(f'Bearer {token}', generated_token)

    @patch('ai_api_client_sdk.helpers.authenticator.requests')
    def test_error(self, requests_mock):
        requests_mock.post.side_effect = Exception
        a = Authenticator(auth_url=self.auth_url, client_id=self.client_id, client_secret=self.client_secret)
        with self.assertRaises(AIAPIAuthenticatorException):
            a.get_token()
        data = {'grant_type': 'client_credentials', 'client_id': self.client_id, 'client_secret': self.client_secret}
        requests_mock.post.assert_called_with(url=self.auth_url, data=data)
