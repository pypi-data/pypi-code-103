from . import get_random_string
from .ai_core_v2_client_e2e_test_base import AICoreV2ClientE2ETestBase

from ai_api_client_sdk.models.label import Label
from ai_core_sdk.models.resource_group import ResourceGroup


class TestE2EResourceGroup(AICoreV2ClientE2ETestBase):

    @staticmethod
    def _get_resource_group(resource_group_id: str):
        return {
            'resource_group_id': resource_group_id,
            'labels': [
                Label(key="ext.ai.sap.com/label1", value="value1"),
                Label(key="ext.ai.sap.com/label2", value="value2"),
            ],
        }

    def create_resource_group(self, resource_group_id: str):
        rg_dict = self._get_resource_group(resource_group_id)
        response = self.ai_core_v2_client.resource_groups.create(
            resource_group_id=rg_dict['resource_group_id'],
            labels=rg_dict['labels'])
        self.assertEqual(rg_dict['resource_group_id'], response.resource_group_id)
        # During create, the resource group labels are not returned, so we can not test them here.

    def delete_resource_group(self, resource_group_id: str):
        response = self.ai_core_v2_client.resource_groups.delete(
            resource_group_id=resource_group_id)
        self.assertEqual(resource_group_id, response.id)
        self.assertIsNotNone(response.message)

    def get_resource_group(self, resource_group_id: str):
        response = self.ai_core_v2_client.resource_groups.get(
            resource_group_id=resource_group_id)
        rg_dict = self._get_resource_group(resource_group_id)
        # We can only be sure about these two fields.
        self.assertEqual(rg_dict['resource_group_id'], response.resource_group_id)
        self.assertEqual(rg_dict['labels'], response.labels)
        # The next fields have halues that are not influenced by us.
        # However, these values must exist.
        self.assertIsNotNone(response.tenant_id)
        self.assertIsNotNone(response.zone_id)
        self.assertIsNotNone(response.status)
        self.assertIsNotNone(response.status_message)

    def modify_resource_group(self, resource_group_id: str):
        labels = [
            Label(key="ext.ai.sap.com/label10", value="value10"),
        ]

        self.ai_core_v2_client.resource_groups.modify(
            resource_group_id=resource_group_id,
            labels=labels)

        # Check that the modification was sucessfull.
        response = self.ai_core_v2_client.resource_groups.get(
            resource_group_id=resource_group_id)
        self.assertEqual(labels, response.labels)

    def query_resource_group(self):
        response = self.ai_core_v2_client.resource_groups.query()
        self.assertGreaterEqual(response.count, 1)
        self.assertGreaterEqual(len(response.resources), 1)
        self.assertIsInstance(response.resources[0], ResourceGroup)

    def test_resource_groups(self):
        resource_group_id = f'trg{get_random_string()[:5]}'
        self.create_resource_group(resource_group_id)
        self.get_resource_group(resource_group_id)
        self.query_resource_group()
        self.modify_resource_group(resource_group_id)
        self.delete_resource_group(resource_group_id)
