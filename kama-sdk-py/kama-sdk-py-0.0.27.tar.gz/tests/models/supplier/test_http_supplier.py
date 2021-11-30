from kama_sdk.model.supplier.ext.misc.http_data_supplier import HttpDataSupplier, ENDPOINT_KEY
from kama_sdk.utils.unittest import helper
from kama_sdk.utils.unittest.base_classes import ClusterTest


class TestHttpSupplier(ClusterTest):

  def test_perform(self):
    instance = HttpDataSupplier.inflate(descriptor)
    actual = instance.resolve()
    self.assertIsNotNone(actual)
    self.assertEqual(200, actual.get('status_code'))
    self.assertEqual(["data"], list(actual.get('body').keys()))


descriptor = {
  ENDPOINT_KEY: helper.http_ktea_uri_with_ver()
}
