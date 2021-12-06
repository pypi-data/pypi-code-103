import copy
import uuid
from datetime import datetime

from .resource_client_test_base import ResourceClientTestBase
from ai_api_client_sdk.helpers.datetime_parser import DATETIME_FORMAT, parse_datetime
from ai_api_client_sdk.models.artifact import Artifact
from ai_api_client_sdk.models.base_models import Order
from ai_api_client_sdk.models.execution import Execution
from ai_api_client_sdk.models.status import Status
from ai_api_client_sdk.models.target_status import TargetStatus
from ai_api_client_sdk.resource_clients.execution_client import ExecutionClient


class TestExecutionClient(ResourceClientTestBase):
    def setUp(self):
        super().setUp()
        self.client = ExecutionClient(self.rest_client_mock)

    @staticmethod
    def create_execution_dict():
        return {
            "id": str(uuid.uuid4()),
            "configuration_id": str(uuid.uuid4()),
            "configuration_name": "test_configuration_name",
            "scenario_id": str(uuid.uuid4()),
            "target_status": "STOPPED",
            "status": "COMPLETED",
            "output_artifacts": [
                {
                    "labels": [
                        {
                            "key": "ext.ai.sap.com/s4hana-version",
                            "value": "label_value"
                        }
                    ],
                    "name": "test_artifact_name",
                    "kind": "model",
                    "url": "https://example.com/some_path",
                    "description": "test_artifact_description",
                    "id": str(uuid.uuid4()),
                    "scenario_id": str(uuid.uuid4()),
                    "execution_id": str(uuid.uuid4()),
                    "created_at": "2021-03-29T12:58:05Z",
                    "modified_at": "2021-03-29T12:58:05Z"
                }
            ],
            "created_at": "2021-03-29T12:58:05Z",
            "modified_at": "2021-03-29T12:58:05Z",
            "submission_time": "2021-03-29T12:58:05Z",
            "start_time": "2021-03-29T12:58:05Z",
            "completion_time": "2021-03-29T12:58:05Z",
            "status_details": {}
        }

    def assert_execution(self, e_dict: dict, e: Execution):
        e_dict['output_artifacts'] = [Artifact.from_dict(oad) for oad in e_dict['output_artifacts']]
        self.assert_enactment(e_dict, e)

    def test_get_execution(self):
        exc_dict = self.create_execution_dict()
        self.rest_client_mock.get.return_value = copy.deepcopy(exc_dict)
        exc = self.client.get(execution_id=exc_dict['id'], resource_group=self.resource_group)
        self.rest_client_mock.get.assert_called_with(path=f'/executions/{exc_dict["id"]}',
                                                     resource_group=self.resource_group)
        self.assert_execution(exc_dict, exc)

    def test_query_executions(self):
        n = 3
        exc_dicts = [self.create_execution_dict() for _ in range(n)]
        self.rest_client_mock.get.return_value = {'resources': copy.deepcopy(exc_dicts), 'count': n}
        eqr = self.client.query()
        self.rest_client_mock.get.assert_called_with(path='/executions', params=None, resource_group=None)
        self.assert_object_lists(exc_dicts, eqr.resources, self.assert_execution)

        params = {'scenario_id': 'test_scenario_id', 'configuration_id': 'test_configuration_id',
                  'executable_ids': ['test_executable_id'], 'status': Status.COMPLETED, 'top': 5, 'skip': 1}
        self.rest_client_mock.get.return_value = {'resources': [], 'count': 0}
        self.client.query(resource_group=self.resource_group, **params)
        params['executable_ids'] = ','.join(params['executable_ids'])
        params['status'] = params['status'].value
        self.rest_client_mock.get.assert_called_with(path='/executions', params=params,
                                                     resource_group=self.resource_group)

    def test_create_execution(self):
        exc_dict = self.create_execution_dict()
        response_message = 'Execution created'
        self.rest_client_mock.post.return_value = {'id': exc_dict['id'], 'message': response_message,
                                                   'status': exc_dict['status']}
        ecr = self.client.create(configuration_id=exc_dict['configuration_id'],
                                 resource_group=self.resource_group)
        body = {"configuration_id": exc_dict['configuration_id']}

        self.rest_client_mock.post.assert_called_with(path='/executions', body=body,
                                                      resource_group=self.resource_group)
        self.assertEqual(exc_dict['id'], ecr.id)
        self.assertEqual(response_message, ecr.message)
        self.assertEqual(Status(exc_dict['status']), ecr.status)

    def test_modify_execution(self):
        response_dict = {'id': 'test_execution_id', 'message': 'Execution patched'}
        body = {'target_status': TargetStatus.STOPPED}
        self.rest_client_mock.patch.return_value = response_dict
        br = self.client.modify(execution_id=response_dict['id'], resource_group=self.resource_group, **body)
        body['target_status'] = body['target_status'].value
        self.rest_client_mock.patch.assert_called_with(path=f'/executions/{response_dict["id"]}', body=body,
                                                       resource_group=self.resource_group)
        self.assertEqual(response_dict['id'], br.id)
        self.assertEqual(response_dict['message'], br.message)

    def test_delete_execution(self):
        response_dict = {'id': 'test_execution_id', 'message': 'Execution deleted'}
        self.rest_client_mock.delete.return_value = response_dict
        br = self.client.delete(execution_id=response_dict['id'], resource_group=self.resource_group)
        self.rest_client_mock.delete.assert_called_with(path=f'/executions/{response_dict["id"]}',
                                                        resource_group=self.resource_group)
        self.assertEqual(response_dict['id'], br.id)
        self.assertEqual(response_dict['message'], br.message)

    def test_count_executions(self):
        self.assert_count('/executions/$count', 7)
        self.assert_count('/executions/$count', 6, {'scenario_id': 'test_scenario_id'})
        self.assert_count('/executions/$count', 5, {'configuration_id': 'test_configuration_id'})
        self.assert_count('/executions/$count', 6, {'executable_ids': ['test_executable_id']})
        self.assert_count('/executions/$count', 3, {'status': Status.COMPLETED})
        self.assert_count('/executions/$count', 0,
                          {'scenario_id': 'test_scenario_id', 'configuration_id': 'test_configuration_id',
                           'executable_ids': ['test_executable_id'], 'status': Status.COMPLETED})

    def test_logs(self):
        execution_id = 'test_execution_id'
        top = 5
        start = datetime.utcnow()
        end = datetime.utcnow()
        order = Order.DESC
        params = {'top': top, 'start': start.strftime(DATETIME_FORMAT), 'end': end.strftime(DATETIME_FORMAT),
                  'order': order.value}
        response_dict = {'data': {'result': [{'msg': 'log message',
                                              'timestamp': '2021-08-27T15:10:36.774534098+00:00'}]}}
        self.rest_client_mock.get.return_value = copy.deepcopy(response_dict)
        lr = self.client.query_logs(execution_id=execution_id, top=top, start=start, end=end, order=order,
                                    resource_group=self.resource_group)
        self.rest_client_mock.get.assert_called_with(path=f'/executions/{execution_id}/logs', params=params,
                                                     resource_group=self.resource_group)
        self.assertEqual(len(response_dict['data']['result']), len(lr.data.result))
        self.assertEqual(response_dict['data']['result'][0]['msg'], lr.data.result[0].msg)
        self.assertEqual(parse_datetime(response_dict['data']['result'][0]['timestamp']), lr.data.result[0].timestamp)
