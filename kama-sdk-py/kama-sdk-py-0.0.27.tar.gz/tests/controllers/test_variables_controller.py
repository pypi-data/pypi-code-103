import json
from typing import Optional, Dict

from flask.testing import FlaskClient

from kama_sdk.cli.server_cli_entrypoint import app
from kama_sdk.core.core.config_man import config_man
from kama_sdk.model.base.mc import KIND_KEY, ID_KEY
from kama_sdk.model.base.models_manager import models_manager
from kama_sdk.model.input.checkboxes_input import SelectInput
from kama_sdk.model.input.generic_input import OPTIONS_KEY
from kama_sdk.model.predicate.predicate import REASON_KEY, OPERATOR_KEY, CHALLENGE_KEY
from kama_sdk.model.variable import generic_variable
from kama_sdk.model.variable.generic_variable import INPUT_MODEL_KEY
from kama_sdk.model.variable.manifest_variable import ManifestVariable
from kama_sdk.utils.unittest import var_test_helpers
from kama_sdk.utils.unittest.base_classes import ClusterTest


def api() -> FlaskClient:
  return app.test_client()


class TestVariablesController(ClusterTest):

  def test_show_without_dependencies(self):
    endpoint = '/api/variables/detail/foo'
    models_manager.add_descriptors([easy_show_descriptor])

    response = api().get(endpoint)
    body = json.loads(response.data).get('data')

    exp_opts = [dict(id='x', title='X'), dict(id='y', title='Y')]
    self.assertEqual('foo', body.get('id'))
    self.assertEqual(SelectInput.__name__, body.get('type'))
    self.assertEqual(exp_opts, body.get('options'))

  def test_show_with_dependencies(self):
    """
    One of the dependencies' activation depends on whether `two`
    equals `x` so we set it up.
    :return:
    """
    config_man.patch_user_vars({'two': {'one': 'x', 'two': 'y'}})
    models_manager.add_descriptors(var_test_helpers.variable_descriptors)
    models_manager.add_descriptors(var_test_helpers.dependency_descriptor)

    endpoint = '/api/variables/detail/one.one'
    response = api().get(endpoint)
    body = json.loads(response.data).get('data')

    def find(var_id: str, list_key: str) -> Optional[Dict]:
      fp = lambda b: b.get('other_variable').get('id') == var_id
      return next(filter(fp, body.get(list_key, [])), None)

    two_one = find('two.one', 'outgoing_dependencies')
    two_two = find('two.two', 'outgoing_dependencies')

    self.assertIsNotNone(two_one)
    self.assertIsNotNone(two_two)

    self.assertFalse(two_one['is_active'])
    self.assertTrue(two_two['is_active'])

  def test_validate_valid(self):
    endpoint = '/api/variables/detail/foo/validate'
    models_manager.add_descriptors([validate_descriptor])

    response = api().post(endpoint, json=dict(value='bar'))
    body = json.loads(response.data).get('data')
    self.assertEqual('valid', body.get('status'))

  def test_validate_not_valid(self):
    endpoint = '/api/variables/detail/foo/validate'
    models_manager.add_descriptors([validate_descriptor])

    response = api().post(endpoint, json=dict(value=''))
    body = json.loads(response.data).get('data')
    self.assertEqual('error', body.get('status'))
    self.assertEqual('Cannot be empty', body.get('message'))

  def test_index(self):
    config_man.patch_user_vars({'foo': 'bar', 'bar': {'foo': 'baz'}})
    models_manager.add_descriptors(index_descriptors)

    response = api().get('/api/variables/all')
    body = json.loads(response.data).get('data')
    cv1, cv2 = body

    self.assertEqual(2, len(body))
    self.assertEqual('foo', cv1.get('id'))
    self.assertEqual('bar', cv1.get('value'))
    self.assertEqual('bar.foo', cv2.get('id'))
    self.assertEqual('baz', cv2.get('value'))


easy_show_descriptor = {
  KIND_KEY: ManifestVariable.__name__,
  ID_KEY: 'foo',
  INPUT_MODEL_KEY: {
    KIND_KEY: SelectInput.__name__,
    OPTIONS_KEY: [
      {'id': 'x', 'title': 'X'},
      {'id': 'y', 'title': 'Y'}
    ]
  }
}

index_descriptors = [
  {
    KIND_KEY: ManifestVariable.__name__,
    ID_KEY: 'foo'
  },
  {
    KIND_KEY: ManifestVariable.__name__,
    ID_KEY: 'bar.foo'
  }
]

validate_descriptor = {
  KIND_KEY: ManifestVariable.__name__,
  ID_KEY: 'foo',
  generic_variable.VALIDATION_PREDS_KEY: [{
    CHALLENGE_KEY: "get::self>>value",
    OPERATOR_KEY: 'presence',
    REASON_KEY: 'Cannot be empty'
  }]
}
