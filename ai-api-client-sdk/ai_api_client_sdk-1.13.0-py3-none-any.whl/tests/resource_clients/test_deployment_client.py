import copy
import uuid
from datetime import datetime

from .resource_client_test_base import ResourceClientTestBase
from ai_api_client_sdk.helpers.datetime_parser import DATETIME_FORMAT, parse_datetime
from ai_api_client_sdk.models.base_models import Order
from ai_api_client_sdk.models.deployment import Deployment
from ai_api_client_sdk.models.status import Status
from ai_api_client_sdk.models.target_status import TargetStatus
from ai_api_client_sdk.resource_clients.deployment_client import DeploymentClient


class TestDeploymentClient(ResourceClientTestBase):
    def setUp(self):
        super().setUp()
        self.client = DeploymentClient(self.rest_client_mock)

    @staticmethod
    def create_deployment_dict():
        return {
            "id": str(uuid.uuid4()),
            "deployment_url": "test_deployment_url",
            "configuration_id": str(uuid.uuid4()),
            "configuration_name": "test_configuration_name",
            "scenario_id": str(uuid.uuid4()),
            "status": "RUNNING",
            "target_status": "RUNNING",
            "created_at": "2021-03-29T12:58:05Z",
            "modified_at": "2021-03-29T12:58:05Z",
            "submission_time": "2021-03-29T12:58:05Z",
            "start_time": "2021-03-29T12:58:05Z",
            "completion_time": "2021-03-29T12:58:05Z",
            "status_details": {}
        }

    def test_get_deployment(self):
        dep_dict = self.create_deployment_dict()
        self.rest_client_mock.get.return_value = dep_dict.copy()
        dep = self.client.get(deployment_id=dep_dict['id'], resource_group=self.resource_group)
        self.rest_client_mock.get.assert_called_with(path=f'/deployments/{dep_dict["id"]}',
                                                     resource_group=self.resource_group)
        self.assert_enactment(dep_dict, dep)

    def test_query_deployments(self):
        n = 3
        dep_dicts = [self.create_deployment_dict() for _ in range(n)]
        self.rest_client_mock.get.return_value = {'resources': [dd.copy() for dd in dep_dicts], 'count': n}
        dqr = self.client.query()
        self.rest_client_mock.get.assert_called_with(path='/deployments', params=None, resource_group=None)
        self.assert_object_lists(dep_dicts, dqr.resources, self.assert_enactment)

        params = {'scenario_id': 'test_scenario_id', 'configuration_id': 'test_configuration_id',
                  'executable_ids': ['test_executable_id'], 'status': Status.RUNNING, 'top': 5, 'skip': 1}
        self.rest_client_mock.get.return_value = {'resources': [], 'count': 0}
        self.client.query(resource_group=self.resource_group, **params)
        params['executable_ids'] = ','.join(params['executable_ids'])
        params['status'] = params['status'].value
        self.rest_client_mock.get.assert_called_with(path='/deployments', params=params,
                                                     resource_group=self.resource_group)

    def test_create_deployment(self):
        dep_dict = self.create_deployment_dict()
        response_message = 'Deployment created'
        self.rest_client_mock.post.return_value = {'id': dep_dict['id'], 'message': response_message,
                                                   'deployment_url': dep_dict['deployment_url'],
                                                   'status': dep_dict['status']}
        dcr = self.client.create(configuration_id=dep_dict['configuration_id'], resource_group=self.resource_group)
        body = {"configuration_id": dep_dict['configuration_id']}
        self.rest_client_mock.post.assert_called_with(path='/deployments', body=body,
                                                      resource_group=self.resource_group)
        self.assertEqual(dep_dict['id'], dcr.id)
        self.assertEqual(response_message, dcr.message)
        self.assertEqual(dep_dict['deployment_url'], dcr.deployment_url)
        self.assertEqual(Status(dep_dict['status']), dcr.status)

    def test_modify_deployment(self):
        response_dict = {'id': 'test_deployment_id', 'message': 'Deployment patched'}
        body = {'target_status': TargetStatus.STOPPED}
        self.rest_client_mock.patch.return_value = response_dict
        br = self.client.modify(deployment_id=response_dict['id'], resource_group=self.resource_group, **body)
        body['target_status'] = body['target_status'].value
        self.rest_client_mock.patch.assert_called_with(path=f'/deployments/{response_dict["id"]}', body=body,
                                                       resource_group=self.resource_group)
        self.assertEqual(response_dict['id'], br.id)
        self.assertEqual(response_dict['message'], br.message)

    def test_delete_deployment(self):
        response_dict = {'id': 'test_deployment_id', 'message': 'Deployment deleted'}
        self.rest_client_mock.delete.return_value = response_dict
        br = self.client.delete(deployment_id=response_dict['id'], resource_group=self.resource_group)
        self.rest_client_mock.delete.assert_called_with(f'/deployments/{response_dict["id"]}',
                                                        resource_group=self.resource_group)
        self.assertEqual(response_dict['id'], br.id)
        self.assertEqual(response_dict['message'], br.message)

    def test_count_deployments(self):
        self.assert_count('/deployments/$count', 7)
        self.assert_count('/deployments/$count', 6, {'scenario_id': 'test_scenario_id'})
        self.assert_count('/deployments/$count', 5, {'configuration_id': 'test_configuration_id'})
        self.assert_count('/deployments/$count', 6, {'executable_ids': ['test_executable_id']})
        self.assert_count('/deployments/$count', 3, {'status': Status.RUNNING})
        self.assert_count('/deployments/$count', 0,
                          {'scenario_id': 'test_scenario_id', 'configuration_id': 'test_configuration_id',
                           'executable_ids': ['test_executable_id'], 'status': Status.RUNNING})

    def test_logs(self):
        deployment_id = 'test_deployment_id'
        top = 5
        start = datetime.utcnow()
        end = datetime.utcnow()
        order = Order.DESC
        params = {'top': top, 'start': start.strftime(DATETIME_FORMAT), 'end': end.strftime(DATETIME_FORMAT),
                  'order': order.value}
        response_dict = {'data': {'result': [{'msg': 'log message',
                                              'timestamp': '2021-08-27T15:10:36.774534098+00:00'}]}}
        self.rest_client_mock.get.return_value = copy.deepcopy(response_dict)
        lr = self.client.query_logs(deployment_id=deployment_id, top=top, start=start, end=end, order=order,
                                    resource_group=self.resource_group)
        self.rest_client_mock.get.assert_called_with(path=f'/deployments/{deployment_id}/logs', params=params,
                                                     resource_group=self.resource_group)
        self.assertEqual(len(response_dict['data']['result']), len(lr.data.result))
        self.assertEqual(response_dict['data']['result'][0]['msg'], lr.data.result[0].msg)
        self.assertEqual(parse_datetime(response_dict['data']['result'][0]['timestamp']), lr.data.result[0].timestamp)
