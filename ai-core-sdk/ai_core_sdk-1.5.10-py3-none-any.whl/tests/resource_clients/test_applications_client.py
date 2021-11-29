import copy

from .resource_client_test_base import ResourceClientTestBase
from ai_core_sdk.exception import AICoreInvalidInputException
from ai_core_sdk.models.application_status import ApplicationStatus
from ai_core_sdk.resource_clients.applications_client import ApplicationsClient


class TestApplicationsClient(ResourceClientTestBase):
    def setUp(self):
        super().setUp()
        self.client = ApplicationsClient(self.rest_client_mock)
        self.app_path = '/admin/applications'

    @staticmethod
    def create_application_dict():
        return {
            'revision': 'test_revision',
            'path': 'test_path',
            'application_name': 'test_app_name',
            'repository_url': 'test_repo_url'
        }

    @staticmethod
    def get_application_status_dict():
        return {
            "health_status": "test_health_status",
            "sync_status": "test_sync_status",
            "message": "test_status_message",
            "source": {
                "repourl": "test_source_repo_url",
                "path": "test_source_path",
                "revision": "test_source_revision"
            },
            "sync_finished_at": "test_sync_finished_at",
            "sync_started_at": "test_sync_started_at",
            "reconciled_at": "test_reconciled_at",
            "sync_ressources_status": [
                {
                  "name": "test_resource_name",
                  "kind": "test_resource_kind",
                  "status": "test_resource_sync_status",
                  "message": "test_resource_sync_message"
                }
            ]
        }

    def assert_application_status(self, status_dict: dict, status: ApplicationStatus):
        sd = copy.deepcopy(status_dict)
        self.assert_object(sd['source'], status.source)
        del sd['source']
        self.assert_object_lists(sd['sync_ressources_status'], status.sync_ressources_status, sort_key='name')
        del sd['sync_ressources_status']
        self.assert_object(sd, status)

    def _test_create_application(self, app_dict: dict):
        response_message = 'application has been been created'
        self.rest_client_mock.post.return_value = {'id': app_dict['application_name'], 'message': response_message}
        response = self.client.create(**app_dict)
        self.rest_client_mock.post.assert_called_with(path=self.app_path, body=app_dict)
        self.assertEqual(response_message, response.message)

    def test_create_application_with_repository_url(self):
        app_dict = self.create_application_dict()
        self._test_create_application(app_dict)

    def test_create_application_with_repository_name(self):
        app_dict = self.create_application_dict()
        del app_dict['repository_url']
        app_dict['repository_name'] = 'test_repository_name'
        self._test_create_application(app_dict)

    def test_create_application_fails_with_both_name_and_url(self):
        app_dict = self.create_application_dict()
        app_dict['repository_name'] = 'test_repository_name'
        with self.assertRaises(AICoreInvalidInputException):
            self.client.create(**app_dict)
        self.rest_client_mock.get.assert_not_called()

    def test_create_application_fails_with_no_name_no_url(self):
        app_dict = self.create_application_dict()
        del app_dict['repository_url']
        with self.assertRaises(AICoreInvalidInputException):
            self.client.create(**app_dict)
        self.rest_client_mock.assert_not_called()

    def test_get_application(self):
        app_dict = self.create_application_dict()
        self.rest_client_mock.get.return_value = app_dict.copy()
        app = self.client.get(application_name=app_dict['application_name'])
        self.rest_client_mock.get.assert_called_with(path=f'{self.app_path}/{app_dict["application_name"]}')
        self.assert_object(app_dict, app)

    def test_get_application_status(self):
        app_name = 'test_app_name'
        status_dict = self.get_application_status_dict()
        self.rest_client_mock.get.return_value = status_dict.copy()
        app_status = self.client.get_status(application_name=app_name)
        self.rest_client_mock.get.assert_called_with(path=f'{self.app_path}/{app_name}/status')
        self.assert_application_status(status_dict, app_status)

    def test_query_applications(self):
        n = 3
        app_dicts = [self.create_application_dict() for _ in range(n)]
        self.rest_client_mock.get.return_value = {'resources': [ad.copy() for ad in app_dicts], 'count': n}
        app_qr = self.client.query()
        self.rest_client_mock.get.assert_called_with(path=self.app_path)
        self.assert_object_lists(app_dicts, app_qr.resources, sort_key='application_name',
                                 assert_object_function=self.assert_object)

    def test_modify_application(self):
        app_dict = self.create_application_dict()
        response_dict = {'id': app_dict['application_name'], 'message': 'application has been updated'}
        self.rest_client_mock.patch.return_value = response_dict
        response = self.client.modify(**app_dict)
        body = app_dict.copy()
        del body['application_name']
        self.rest_client_mock.patch.assert_called_with(path=f'{self.app_path}/{app_dict["application_name"]}',
                                                       body=body)
        self.assert_object(response_dict, response)

    def test_delete_application(self):
        app_name = 'test_app_name'
        response_dict = {'id': app_name, 'message': 'application deleted'}
        self.rest_client_mock.delete.return_value = response_dict
        response = self.client.delete(application_name=app_name)
        self.rest_client_mock.delete.assert_called_with(path=f'{self.app_path}/{app_name}')
        self.assert_object(response_dict, response)
