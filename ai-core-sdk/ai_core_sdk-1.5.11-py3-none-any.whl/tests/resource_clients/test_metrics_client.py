from unittest.mock import MagicMock

from ai_api_client_sdk.models.metric import Metric
from ai_api_client_sdk.models.metric_custom_info import MetricCustomInfo
from ai_api_client_sdk.models.metric_tag import MetricTag

from .resource_client_test_base import ResourceClientTestBase
from ai_core_sdk.resource_clients.metrics_client import MetricsCoreClient


class TestMetricsCoreClient(ResourceClientTestBase):
    def setUp(self):
        self.rest_client_mock = MagicMock()
        self.metrics_client = MetricsCoreClient(self.rest_client_mock)

    @staticmethod
    def __patch_metrics_body(execution_id):
        patch_mb = {
            "execution_id": execution_id,
            "metrics": [
                {
                    "name": "Test Error Rate",
                    "value": 0.98,
                    "timestamp": "2021-06-10T06:22:19Z",
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
                    "name": "Test Artifact Group",
                    "value": "RFC-1"
                }
            ],
            "custom_info": [
                {
                    "name": "Test Confusion Matrix",
                    "value": "[{'Predicted': 'False',  'Actual': 'False','value': 34}]"
                }
            ]
        }
        return patch_mb

    def test_modify_metrics(self):
        metrics_patch_data = self.__patch_metrics_body(execution_id='test_execution_id')
        body = {'execution_id': metrics_patch_data.get('execution_id'),
                'metrics': [Metric.from_dict(md) for md in metrics_patch_data['metrics']],
                'tags': [MetricTag.from_dict(mtd) for mtd in metrics_patch_data['tags']],
                'custom_info': [MetricCustomInfo.from_dict(mcid) for mcid in metrics_patch_data['custom_info']]}
        self.metrics_client.modify(**body, resource_group=self.resource_group)

        self.rest_client_mock.patch.assert_called_with(path='/metrics',
                                                       body=self.__patch_metrics_body(execution_id='test_execution_id'),
                                                       resource_group=self.resource_group)
