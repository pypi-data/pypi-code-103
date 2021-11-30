import json

from kama_sdk.core.core.config_man import config_man, INSTALL_ID_KEY, INSTALL_TOKEN_KEY, SPACE_KW
from kama_sdk.cli.server_cli_entrypoint import app
from kama_sdk.core.core.plugin_type_defs import PluginManifest
from kama_sdk.core.core.plugins_manager import plugins_manager
from kama_sdk.utils.unittest.base_classes import ClusterTest


class TestPluginsController(ClusterTest):

  def test_index_trivial(self):
    plugins_manager.register_manifest(my_plugin)
    endpoint = '/api/plugins/all'
    response = app.test_client().get(endpoint)
    body = json.loads(response.data).get('data')
    self.assertEqual('my', body[0].get('id'))
    self.assertEqual('test-app', body[0].get('app_identifier'))
    self.assertEqual('test-pub', body[0].get('publisher_identifier'))

  def test_index_with_some_data(self):
    config_man.write_typed_entries({
      INSTALL_ID_KEY: 'id',
      INSTALL_TOKEN_KEY: 'token'
    }, **{SPACE_KW: 'my'})
    plugins_manager.register_manifest(my_plugin)

    endpoint = '/api/plugins/all'
    response = app.test_client().get(endpoint)
    body = json.loads(response.data).get('data')

    self.assertEqual('id', body[0].get('install_id'))
    self.assertEqual('token', body[0].get('install_token'))


my_plugin = PluginManifest(
  id='my',
  app_identifier='test-app',
  publisher_identifier='test-pub'
)
