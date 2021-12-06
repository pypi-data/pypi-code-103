import copy
import uuid
from unittest.mock import MagicMock

from .resource_client_test_base import ResourceClientTestBase
from ai_api_client_sdk.models.metric import Metric
from ai_api_client_sdk.models.metric_custom_info import MetricCustomInfo
from ai_api_client_sdk.models.metric_resource import MetricResource
from ai_api_client_sdk.models.metric_tag import MetricTag
from ai_api_client_sdk.resource_clients.metrics_client import MetricsClient


class TestMetricsClient(ResourceClientTestBase):
    def setUp(self):
        n = 3
        self.metric_resource_dicts = [self.create_metric_resource_dict() for _ in range(n)]
        self.rest_client_mock = MagicMock()
        self.rest_client_mock.get.return_value = {'resources': copy.deepcopy(self.metric_resource_dicts), 'count': n}
        self.mc = MetricsClient(self.rest_client_mock)

    @staticmethod
    def create_metric_resource_dict():
        return {
            "execution_id": str(uuid.uuid4()),
            "metrics": [
                {
                    "name": "Error Rate",
                    "value": 0.98,
                    "timestamp": "2021-03-29T12:58:05Z",
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
            "custom_info": [
                {
                    "name": "Confusion Matrix",
                    "value": "test_confusion_matrix"
                }
            ]
        }

    def assert_metric_resources(self, mr_dict: dict, mr: MetricResource):
        mr_dict['metrics'] = [Metric.from_dict(md) for md in mr_dict['metrics']]
        mr_dict['tags'] = [MetricTag.from_dict(mtd) for mtd in mr_dict['tags']]
        mr_dict['custom_info'] = [MetricCustomInfo.from_dict(mcid) for mcid in mr_dict['custom_info']]
        self.assert_object(mr_dict, mr)

    def test_query_metrics(self):
        params = {'$filter': 'test_filter', 'execution_ids': ['test_exec_id']}

        mqr = self.mc.query(filter=params['$filter'], execution_ids=params['execution_ids'],
                            resource_group=self.resource_group)
        params['execution_ids'] = ','.join(params['execution_ids'])
        self.rest_client_mock.get.assert_called_with(path='/metrics', params=params, resource_group=self.resource_group)
        self.assert_object_lists(self.metric_resource_dicts, mqr.resources, self.assert_metric_resources,
                                 sort_key='execution_id')

    def test_query_with_only_execution_ids(self):
        params = {'execution_ids': ['test_exec_id']}
        mqr = self.mc.query(execution_ids=params['execution_ids'], resource_group=self.resource_group)
        params['execution_ids'] = ','.join(params['execution_ids'])
        self.rest_client_mock.get.assert_called_with(path='/metrics', params=params, resource_group=self.resource_group)
        self.assert_object_lists(self.metric_resource_dicts, mqr.resources, self.assert_metric_resources,
                                 sort_key='execution_id')

    def test_query_metrics_with_no_parameters(self):
        mqr = self.mc.query(resource_group=self.resource_group)
        self.rest_client_mock.get.assert_called_with(path='/metrics', params=None, resource_group=self.resource_group)
        self.assert_object_lists(self.metric_resource_dicts, mqr.resources, self.assert_metric_resources,
                                 sort_key='execution_id')

    def test_delete_metrics(self):
        execution_id = 'test_exec_id'
        self.mc.delete(execution_id=execution_id, resource_group=self.resource_group)
        params = {'execution_id': execution_id}
        self.rest_client_mock.delete.assert_called_with(path='/metrics', params=params,
                                                        resource_group=self.resource_group)
