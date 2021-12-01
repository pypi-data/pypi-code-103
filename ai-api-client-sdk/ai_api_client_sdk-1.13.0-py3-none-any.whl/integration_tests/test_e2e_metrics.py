from .ai_api_v2_client_e2e_test_base import AIAPIV2ClientE2ETestBase
from ai_api_client_sdk.exception import AIAPINotFoundException, AIAPIInvalidRequestException
import requests
from . import get_token, RESOURCE_GROUP_ID, BASE_URL


class TestE2EMetrics(AIAPIV2ClientE2ETestBase):
    def setUp(self) -> None:
        super().setUp()
        configuration = self.get_a_configuration(deployable=False)
        res = self.ai_api_v2_client.execution.create(configuration_id=configuration.id)
        self.execution_id = res.id
        self.__post_metrics_for_execution(self.execution_id)

    def test_query_metrics(self):
        with self.assertRaises(AIAPINotFoundException):
            execution_id = "not-exist"
            self.ai_api_v2_client.metrics.query(execution_ids=[execution_id])
        response = self.ai_api_v2_client.metrics.query(execution_ids=[self.execution_id])
        metric = response.resources[0]
        self.__assert_metric_returned(metric, self.execution_id)
        response = self.ai_api_v2_client.metrics.query(filter=f"executionId eq '{self.execution_id}'")
        metric = response.resources[0]
        self.__assert_metric_returned(metric, self.execution_id)
        with self.assertRaises(AIAPIInvalidRequestException):
            self.ai_api_v2_client.metrics.query(filter=f"executionId eq '{self.execution_id}'",
                                                execution_ids=[self.execution_id])

    def test_delete_metrics(self):
        with self.assertRaises(AIAPINotFoundException):
            execution_id = "aa97b177-9383-4934-8543-0f91b7a0283a"
            self.ai_api_v2_client.metrics.delete(execution_id=execution_id)
        response = self.ai_api_v2_client.metrics.query(execution_ids=[self.execution_id])
        metric = response.resources[0]
        self.__assert_metric_returned(metric, self.execution_id)
        self.ai_api_v2_client.metrics.delete(execution_id=self.execution_id)
        with self.assertRaises(AIAPINotFoundException):
            self.ai_api_v2_client.metrics.query(execution_ids=[self.execution_id])

    def __assert_metric_returned(self, metric, execution_id):
        self.assertEqual(metric.execution_id, execution_id)
        self.assertIsNotNone(metric.metrics)
        self.assertIsNotNone(metric.tags)
        self.assertIsNotNone(metric.custom_info)

    @staticmethod
    def __post_metrics_for_execution(execution_id):
        headers = {'Authorization': get_token(), 'AI-Resource-Group': RESOURCE_GROUP_ID}
        metrics = {
            "executionId": execution_id,
            "metrics": [
                {
                    "name": "Error Rate",
                    "value": 0.98,
                    "timestamp": "2021-06-10T06:22:19.412Z",
                    "step": 2,
                    "labels": [
                        {
                            "name": "group",
                            "value": "tree-82"
                        }
                    ]
                }
            ],
            "tags": [
                {
                    "name": "Artifact Group",
                    "value": "RFC-1"
                }
            ],
            "customInfo": [
                {
                    "name": "Confusion Matrix",
                    "value": "[{'Predicted': 'False',  'Actual': 'False','value': 34}]"
                }
            ]
        }
        response = requests.patch(url=f'{BASE_URL}/metrics', json=metrics, headers=headers)
        if response.status_code != 204:
            raise Exception(f"Failed to post metrics for execution {execution_id}")
        print(f'Successfully add metrics for execution {execution_id} in testing')
