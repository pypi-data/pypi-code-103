import time

from k8kat.utils.testing import ns_factory

from kama_sdk.utils import utils
from kama_sdk.core.core.config_man import config_man
from kama_sdk.core.ktea.ktea_client import KteaClient
from kama_sdk.utils.unittest import helper
from kama_sdk.utils.unittest.base_classes import ClusterTest


class Base:
  class TestKteaSuper(ClusterTest):

    def client_instance(self) -> KteaClient:
      raise RuntimeError

    def setUp(self) -> None:
      super().setUp()
      self.ns, = ns_factory.request(1)
      helper.mock_globals(self.ns)
      helper.create_base_kamafile(self.ns)

    def tearDown(self) -> None:
      super().tearDown()
      ns_factory.relinquish(self.ns)

    def test_load_manifest_defaults(self):
      time.sleep(3)
      values = self.client_instance().load_default_values()
      self.assertEqual(exp_default_values, values)

    def test_template_manifest(self):
      time.sleep(3)
      config_man.patch_user_vars(manifest_vars)

      values = utils.deep_merge(
        manifest_vars,
        utils.flat2deep(flat_inlines)
      )

      result = self.client_instance().template_manifest(
        values
      )

      kinds = sorted([r['kind'] for r in result])
      svc = [r for r in result if r['kind'] == 'Service'][0]
      pod = [r for r in result if r['kind'] == 'Pod'][0]

      self.assertEqual(len(result), 2)
      self.assertEqual(sorted(['Pod', 'Service']), kinds)
      self.assertEqual('inline', svc['metadata']['name'])
      self.assertEqual('updated-pod', pod['metadata']['name'])


manifest_vars = {
  'pod': {
    'name': 'updated-pod',
  },
  'service': {
    'port': 81
  }
}


flat_inlines = {
  'service.name': 'inline'
}


exp_default_values = {
  'service': {
    'name': 'service',
    'port': 80
  },
  'pod': {
    'name': 'pod',
    'image': 'nginx'
  }
}
