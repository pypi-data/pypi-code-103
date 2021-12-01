import json
from unittest import TestCase
from unittest.mock import MagicMock, patch

from ai_api_client_sdk.exception import AIAPIAuthorizationException, AIAPIInvalidRequestException, \
    AIAPINotFoundException, AIAPIPreconditionFailedException, AIAPIRequestException, AIAPIServerException
from ai_api_client_sdk.helpers.rest_client import RestClient

REQUESTS_PATCH_STRING = 'ai_api_client_sdk.helpers.rest_client.requests'


class TestRestClient(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.base_url = 'test_base_url'
        cls.resource_group = 'test_resource_group'
        cls.path = '/test_path'
        cls.url = f'{cls.base_url}{cls.path}'
        cls.params = {'param1': 'value1'}
        cls.body = {'key': 'value'}
        cls.headers = {'AI-Resource-Group': cls.resource_group, 'Authorization': cls.get_token()}
        cls.response_json = {'response': 'OK'}
        cls.response_mock = cls.create_response_mock(200, cls.response_json)
        cls.rest_client = RestClient(base_url=cls.base_url, get_token=cls.get_token, resource_group=cls.resource_group)

    @staticmethod
    def create_response_mock(status_code, json_dict, text=None):
        response_mock = MagicMock()
        response_mock.status_code = status_code
        response_mock.json.return_value = json_dict
        if text is None:
            response_mock.text = json.dumps(json_dict)
        else:
            response_mock.text = text
        return response_mock

    @staticmethod
    def create_error_json(message=None, code=None, request_id=None, details=None):
        error_json = {
            'error': {
                'message': message if message else 'Error message',
                'code': code if code else 'Error code',
                'requestId': request_id if request_id else 'request_id'
            }
        }
        if details:
            error_json['error']['details'] = details
        return error_json

    def create_error_description(self, path=None):
        path = path or self.path
        return f'Failed to get {path}'

    def assert_server_exception(self, exception: AIAPIServerException, status_code: int, error_description: str = None,
                                error_json: dict = None, response_text: str = None):
        self.assertEqual(status_code, exception.status_code)
        error_description = error_description or self.create_error_description()
        self.assertEqual(error_description, exception.description)
        if response_text:
            self.assertEqual(response_text, exception.error_message)
        if error_json:
            self.assertEqual(error_json['error']['message'], exception.error_message)
            self.assertEqual(error_json['error']['code'], exception.error_code)
            self.assertEqual(error_json['error']['requestId'], exception.request_id)
            self.assertEqual(error_json['error'].get('details'), exception.details)

    @staticmethod
    def get_token():
        return 'test_token'

    @patch(REQUESTS_PATCH_STRING)
    def test_get(self, requests_mock):
        requests_mock.get.return_value = self.response_mock
        r_json = self.rest_client.get(path=self.path, params=self.params)
        requests_mock.get.assert_called_with(url=self.url, params=self.params, json=None, headers=self.headers)
        self.assertEqual(self.response_json, r_json)

    @patch(REQUESTS_PATCH_STRING)
    def test_get_empty_body(self, requests_mock):
        requests_mock.get.return_value = self.create_response_mock(200, None, '')
        requests_mock.get.return_value.json.side_effect = json.decoder.JSONDecodeError('msg', 'doc', 1)
        r_json = self.rest_client.get(path=self.path, params=self.params)
        requests_mock.get.assert_called_with(url=self.url, params=self.params, json=None, headers=self.headers)
        self.assertEqual('', r_json)

    @patch(REQUESTS_PATCH_STRING)
    def test_post(self, requests_mock):
        requests_mock.post.return_value = self.response_mock
        r_json = self.rest_client.post(path=self.path, body=self.body)
        requests_mock.post.assert_called_with(url=self.url, params=None, json=self.body, headers=self.headers)
        self.assertEqual(self.response_json, r_json)

    @patch(REQUESTS_PATCH_STRING)
    def test_post_empty_body(self, requests_mock):
        requests_mock.post.return_value = self.create_response_mock(200, None, '')
        requests_mock.post.return_value.json.side_effect = json.decoder.JSONDecodeError('msg', 'doc', 1)
        r_json = self.rest_client.post(path=self.path, body=self.body)
        requests_mock.post.assert_called_with(url=self.url, params=None, json=self.body, headers=self.headers)
        self.assertEqual('', r_json)

    @patch(REQUESTS_PATCH_STRING)
    def test_patch(self, requests_mock):
        requests_mock.patch.return_value = self.response_mock
        r_json = self.rest_client.patch(path=self.path, body=self.body)
        requests_mock.patch.assert_called_with(url=self.url, params=None, json=self.body, headers=self.headers)
        self.assertEqual(self.response_json, r_json)

    @patch(REQUESTS_PATCH_STRING)
    def test_patch_empty_body(self, requests_mock):
        requests_mock.patch.return_value = self.create_response_mock(200, None, '')
        requests_mock.patch.return_value.json.side_effect = json.decoder.JSONDecodeError('msg', 'doc', 1)
        r_json = self.rest_client.patch(path=self.path, body=self.body)
        requests_mock.patch.assert_called_with(url=self.url, params=None, json=self.body, headers=self.headers)
        self.assertEqual('', r_json)

    @patch(REQUESTS_PATCH_STRING)
    def test_delete(self, requests_mock):
        requests_mock.delete.return_value = self.response_mock
        r_json = self.rest_client.delete(path=self.path)
        requests_mock.delete.assert_called_with(url=self.url, params=None, json=None, headers=self.headers)
        self.assertEqual(self.response_json, r_json)

    @patch(REQUESTS_PATCH_STRING)
    def test_delete_empty_body(self, requests_mock):
        requests_mock.delete.return_value = self.create_response_mock(200, None, '')
        requests_mock.delete.return_value.json.side_effect = json.decoder.JSONDecodeError('msg', 'doc', 1)
        r_json = self.rest_client.delete(path=self.path)
        requests_mock.delete.assert_called_with(url=self.url, params=None, json=None, headers=self.headers)
        self.assertEqual('', r_json)

    @patch(REQUESTS_PATCH_STRING)
    def test_get_with_resource_group(self, requests_mock):
        requests_mock.get.return_value = self.response_mock
        new_rg = 'new_resource_group'
        headers = self.headers.copy()
        headers['AI-Resource-Group'] = new_rg
        r_json = self.rest_client.get(path=self.path, resource_group=new_rg)
        requests_mock.get.assert_called_with(url=self.url, params=None, json=None, headers=headers)
        self.assertEqual(self.response_json, r_json)

    @patch(REQUESTS_PATCH_STRING)
    def test_camelize_decamelize(self, requests_mock):
        body = {'body_key': 'body_value'}
        c_body = {'bodyKey': 'body_value'}
        params = {'param_key': 'param_value'}
        c_params = {'paramKey': 'param_value'}
        response_json = {'responseKey': 'response_value'}
        d_response_json = {'response_key': 'response_value'}
        requests_mock.post.return_value = self.create_response_mock(200, response_json)
        r_json = self.rest_client.post(path=self.path, body=body)
        requests_mock.post.assert_called_with(url=self.url, params=None, json=c_body, headers=self.headers)
        self.assertEqual(d_response_json, r_json)

        requests_mock.get.return_value = self.create_response_mock(200, response_json)
        r_json = self.rest_client.get(path=self.path, params=params)
        requests_mock.get.assert_called_with(url=self.url, params=c_params, json=None, headers=self.headers)
        self.assertEqual(d_response_json, r_json)

    @patch(REQUESTS_PATCH_STRING)
    def test_authorization_exception(self, requests_mock):
        requests_mock.get.return_value = self.create_response_mock(401, {})
        with self.assertRaises(AIAPIAuthorizationException) as cm:
            self.rest_client.get(path=self.path)
        requests_mock.get.assert_called_with(url=self.url, params=None, json=None, headers=self.headers)
        self.assertEqual(f'Failed to get {self.path}', cm.exception.description)

    @patch(REQUESTS_PATCH_STRING)
    def test_request_exception(self, requests_mock):
        requests_mock.get.side_effect = Exception
        with self.assertRaises(AIAPIRequestException):
            self.rest_client.get(path=self.path)

    @patch(REQUESTS_PATCH_STRING)
    def test_server_exception(self, requests_mock):
        status_code = 500
        response_text = 'error_text'
        requests_mock.get.return_value = self.create_response_mock(status_code, {}, response_text)
        with self.assertRaises(AIAPIServerException) as cm:
            self.rest_client.get(path=self.path)
        self.assert_server_exception(cm.exception, status_code, response_text=response_text)

    @patch(REQUESTS_PATCH_STRING)
    def test_invalid_request_exception(self, requests_mock):
        status_code = 400
        error_json = self.create_error_json(message='Invalid Request', details='Invalid')
        requests_mock.get.return_value = self.create_response_mock(status_code, error_json)
        with self.assertRaises(AIAPIInvalidRequestException) as cm:
            self.rest_client.get(path=self.path)
        self.assert_server_exception(cm.exception, status_code, error_json=error_json)

    @patch(REQUESTS_PATCH_STRING)
    def test_not_found_exception(self, requests_mock):
        status_code = 404
        error_json = self.create_error_json(message='Not Found')
        requests_mock.get.return_value = self.create_response_mock(status_code, error_json)
        with self.assertRaises(AIAPINotFoundException) as cm:
            self.rest_client.get(path=self.path)
        self.assert_server_exception(cm.exception, status_code, error_json=error_json)

    @patch(REQUESTS_PATCH_STRING)
    def test_precondition_failed_exception(self, requests_mock):
        status_code = 412
        error_json = self.create_error_json(message='Precondition Failed')
        requests_mock.get.return_value = self.create_response_mock(status_code, error_json)
        with self.assertRaises(AIAPIPreconditionFailedException) as cm:
            self.rest_client.get(path=self.path)
        self.assert_server_exception(cm.exception, status_code, error_json=error_json)
