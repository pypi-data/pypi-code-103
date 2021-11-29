from ai_api_client_sdk.models.label import Label
from ai_core_sdk.models.resource_group import ResourceGroup
from ai_core_sdk.models.resource_group_query_response import ResourceGroupQueryResponse
from .resource_client_test_base import ResourceClientTestBase
from ai_core_sdk.resource_clients.resource_groups_client import ResourceGroupsClient


class TestDockerRegistrySecretsClient(ResourceClientTestBase):
    def setUp(self):
        super().setUp()
        self.client = ResourceGroupsClient(self.rest_client_mock)
        self.rg_path = '/admin/resourceGroups'

    def assert_resource_group(self, rg_expected: ResourceGroup, rg: ResourceGroup):
        self.assertEqual(rg_expected.resource_group_id, rg.resource_group_id)
        self.assertEqual(rg_expected.labels, rg.labels)

    @staticmethod
    def create_resource_group_dict():
        return {
            'resource_group_id': 'testrg',
            'tenant_id': 'test_tenant_id',
            'zone_id': 'test_zone_id',
            'labels': [
                {
                    'key': 'ext.ai.sap.com/label1',
                    'value': 'value1',
                },
                {
                    'key': 'ext.ai.sap.com/label2',
                    'value': 'value2',
                },
            ],
            'status': 'test_status',
            'status_message': 'test_status_message',
        }

    @staticmethod
    def create_resource_group():
        return ResourceGroup.from_dict(TestDockerRegistrySecretsClient.create_resource_group_dict())

    def test_create_resource_group(self):
        self.rest_client_mock.post.return_value = self.create_resource_group_dict()
        rg = self.create_resource_group()
        response = self.client.create(resource_group_id=rg.resource_group_id, labels=rg.labels)
        body = {
            'resourceGroupId': rg.resource_group_id,
            'labels': [l.to_dict() for l in rg.labels],
        }
        self.rest_client_mock.post.assert_called_with(path=self.rg_path, body=body)
        self.assert_resource_group(rg, response)

    def test_delete_resource_group(self):
        test_rg_name = 'test_resource_group_name'
        response_dict = {
            'id': test_rg_name,
            'message': 'Resource Group deleted',
        }
        self.rest_client_mock.delete.return_value = response_dict
        br = self.client.delete(resource_group_id=test_rg_name)
        self.rest_client_mock.delete.assert_called_with(path=f'{self.rg_path}/{test_rg_name}')
        self.assertEqual(response_dict['id'], br.id)
        self.assertEqual(response_dict['message'], br.message)

    def test_get_resource_group(self):
        rg_dict = self.create_resource_group_dict()
        resource_group_id = rg_dict['resource_group_id']
        self.rest_client_mock.get.return_value = rg_dict.copy()
        rg = self.client.get(resource_group_id=resource_group_id)
        self.rest_client_mock.get.assert_called_with(path=f'{self.rg_path}/{resource_group_id}')

        expected_rg = self.create_resource_group()
        self.assertEqual(expected_rg.resource_group_id, rg.resource_group_id)
        self.assertEqual(expected_rg.labels, rg.labels)
        self.assertEqual(expected_rg.tenant_id, rg.tenant_id)
        self.assertEqual(expected_rg.zone_id, rg.zone_id)
        self.assertEqual(expected_rg.status, rg.status)
        self.assertEqual(expected_rg.status_message, rg.status_message)

    def test_modify_resource_group(self):
        rg = self.create_resource_group()
        self.rest_client_mock.modify.return_value = ""
        self.client.modify(resource_group_id=rg.resource_group_id, labels=rg.labels)
        body = {
            'resourceGroupId': rg.resource_group_id,
            'labels': [l.to_dict() for l in rg.labels],
        }
        self.rest_client_mock.patch.assert_called_with(path=f'{self.rg_path}/{rg.resource_group_id}', body=body)

    def test_query_resource_group(self):
        self.rest_client_mock.get.return_value = {
            'resources': [
                self.create_resource_group_dict(),
            ],
            'count': 1,
        }
        response = self.client.query()
        self.rest_client_mock.get.assert_called_with(path=f'{self.rg_path}')

        expected_response = ResourceGroupQueryResponse([self.create_resource_group()], 1)
        self.assertEqual(expected_response.count, response.count)
        self.assertEqual(len(expected_response.resources), len(response.resources))

        resource0 = response.resources[0]
        expected_resource0 = expected_response.resources[0]
        self.assertEqual(expected_resource0.resource_group_id, resource0.resource_group_id)
        self.assertEqual(expected_resource0.labels, resource0.labels)
        self.assertEqual(expected_resource0.tenant_id, resource0.tenant_id)
        self.assertEqual(expected_resource0.zone_id, resource0.zone_id)
        self.assertEqual(expected_resource0.status, resource0.status)
        self.assertEqual(expected_resource0.status_message, resource0.status_message)
