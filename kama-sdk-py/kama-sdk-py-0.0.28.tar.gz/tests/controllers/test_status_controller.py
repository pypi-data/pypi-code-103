import json

from kama_sdk.cli.server_cli_entrypoint import app
from kama_sdk.utils.unittest.base_classes import ClusterTest


class TestStatusController(ClusterTest):

  def test_ping(self):
    response = app.test_client().get('/api/ping')
    body = json.loads(response.data)
    self.assertEqual(body, dict(ping='pong'))

  def test_status(self):
    response = app.test_client().get('/api/status')
    ret_data = json.loads(response.data)
    self.assertIsNotNone(ret_data)
