from typing import List

from ai_api_client_sdk.exception import AIAPIInvalidRequestException
from ai_api_client_sdk.models.artifact import Artifact
from ai_api_client_sdk.models.input_artifact import InputArtifact
from ai_api_client_sdk.models.input_artifact_binding import InputArtifactBinding
from ai_api_client_sdk.models.label import Label
from ai_api_client_sdk.models.metric import Metric
from ai_api_client_sdk.models.metric_custom_info import MetricCustomInfo
from ai_api_client_sdk.models.metric_tag import MetricTag
from ai_api_client_sdk.models.parameter import Parameter
from ai_api_client_sdk.models.parameter_binding import ParameterBinding

from .ai_core_v2_client_e2e_test_base import AICoreV2ClientE2ETestBase


class TestE2EMetrics(AICoreV2ClientE2ETestBase):

    def setUp(self):
        super().setUp()
        configuration = self.get_configuration()
        res = self.ai_core_v2_client.execution.create(configuration_id=configuration.id)
        self.execution_id = res.id

    def create_configuration_dict(self, executable_id: str, parameters: List[Parameter] = None,
                                  input_artifacts: List[InputArtifact] = None):
        configuration_dict = {
            "name": "configuration_name",
            "executable_id": executable_id,
            "scenario_id": self.test_scenario_id
        }
        if parameters:
            configuration_dict['parameter_bindings'] = [
                ParameterBinding(key=p.name, value=f'Test {p.name} value') for p in parameters
            ]
        if input_artifacts:
            artifact = self.get_an_artifact()
            configuration_dict['input_artifact_bindings'] = [
                InputArtifactBinding(key=ia.name, artifact_id=artifact.id) for ia in input_artifacts
            ]
        return configuration_dict

    def create_artifact_dict(self, i=1, labels=None, kind: Artifact.Kind = Artifact.Kind.MODEL):
        if not labels:
            labels = [
                Label(**{
                    "key": "ext.ai.sap.com/s4hana-version",
                    "value": "string"
                })
            ]
        return {
            'name': f'Test Artifact {i}',
            'kind': kind,
            'labels': labels,
            'url': 'gs://kfserving-samples/models/tensorflow/flowers',
            'scenario_id': self.test_scenario_id,
            'description': f'Test Artifact {i} description'
        }

    def get_an_artifact(self):
        res = self.ai_core_v2_client.artifact.query(scenario_id=self.test_scenario_id)
        if res.count > 0:
            return res.resources[0]
        artifact_dict = self.create_artifact_dict()
        res = self.ai_core_v2_client.artifact.create(**artifact_dict)
        return self.ai_core_v2_client.artifact.get(artifact_id=res.id)

    def get_executable(self):
        res = self.ai_core_v2_client.executable.query(scenario_id=self.test_scenario_id)
        self.assertEqual(res.count, len(res.resources))
        self.assertTrue(res.count > 0)
        executables = res.resources
        for e in executables:
            if not e.deployable:
                return e

    def get_configuration(self):
        executable = self.get_executable()
        configuration_dict = self.create_configuration_dict(executable_id=executable.id,
                                                            parameters=executable.parameters,
                                                            input_artifacts=executable.input_artifacts)
        res = self.ai_core_v2_client.configuration.create(**configuration_dict)
        return self.ai_core_v2_client.configuration.get(configuration_id=res.id)

    @staticmethod
    def __patch_metrics_body(execution_id):
        patch_mb = {
            "executionId": execution_id,
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
            "customInfo": [
                {
                    "name": "Test Confusion Matrix",
                    "value": "[{'Predicted': 'False',  'Actual': 'False','value': 34}]"
                }
            ]
        }
        return patch_mb

    def test_patch_metrics(self):
        metrics_patch_data = self.__patch_metrics_body(self.execution_id)
        body = {'execution_id': metrics_patch_data.get('executionId'),
                'metrics': [Metric.from_dict(md) for md in metrics_patch_data['metrics']],
                'tags': [MetricTag.from_dict(mtd) for mtd in metrics_patch_data['tags']],
                'custom_info': [MetricCustomInfo.from_dict(mcid) for mcid in metrics_patch_data['customInfo']]}
        self.ai_core_v2_client.metrics.modify(**body)
        response = self.ai_core_v2_client.metrics.query(execution_ids=[self.execution_id])
        metric_resource = response.resources[response.count - 1]
        metric_dict = {}
        metric_dict['execution_id'] = metric_resource.execution_id
        self.assertIsNotNone(metric_resource.metrics)
        self.assertIsNotNone(metric_resource.tags)
        self.assertIsNotNone(metric_resource.custom_info)
        metric_dict['metrics'] = [metric.__dict__ for metric in metric_resource.metrics]
        metric_dict['tags'] = [tag.__dict__ for tag in metric_resource.tags]
        metric_dict['custom_info'] = [c_info.__dict__ for c_info in metric_resource.custom_info]
        self.assertEqual(metric_dict['execution_id'], metrics_patch_data['executionId'])
        self.assertEqual(metric_dict['metrics'], metrics_patch_data['metrics'])
        self.assertEqual(metric_dict['tags'], metrics_patch_data['tags'])
        self.assertEqual(metric_dict['custom_info'], metrics_patch_data['customInfo'])
        with self.assertRaises(AIAPIInvalidRequestException):
            self.ai_core_v2_client.metrics.modify(execution_id='')
