import json

from kama_sdk.model.base.models_manager import models_manager
from kama_sdk.model.operation.operation import Operation
from kama_sdk.model.operation.operation_state import OperationState
from kama_sdk.model.predicate.format_predicate import FormatPredicate
from kama_sdk.model.predicate.predicate import Predicate
from kama_sdk.cli.server_cli_entrypoint import app
from kama_sdk.utils.unittest import helper
from kama_sdk.utils.unittest.base_classes import ClusterTest


class TestOperationsController(ClusterTest):

  def setUp(self) -> None:
    models_manager.add_any_descriptors([basic_operation_config])
    OperationState.clear_list()

    endpoint = f'{operation_path}/generate-ost'
    response = app.test_client().post(endpoint)
    self.ost = json.loads(response.data)['data']

  def test_operations_index(self):
    config = helper.g_conf(k='foo', t='Foo', i='Operation')
    models_manager.add_any_descriptors([config])

    response = app.test_client().get('/api/operations')
    data = json.loads(response.data).get('data')
    self.assertEqual(200, response.status_code)
    self.assertEqual(1, len(data))


operation_path = '/api/operations/unittest'
steps_path = f'{operation_path}/steps'


basic_operation_config = dict(
  kind=Operation.__name__,
  id='unittest',
  labels=dict(
    searchable=True
  ),
  steps=[
    dict(
      id='step-1',
      fields=[
        dict(
          id='field-11',
          validation=[
            dict(
              kind=FormatPredicate.__name__,
              check_against='email'
            )
          ],
        ),
        dict(
          id='field-12',
          visible=dict(
            kind=Predicate.__name__,
            challenge='get::self>>inputs->.field-11',
            check_against='on'
          )
        )
      ]
    )
  ]
)
