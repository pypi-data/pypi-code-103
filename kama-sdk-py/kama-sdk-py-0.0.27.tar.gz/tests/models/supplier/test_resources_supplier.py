from k8kat.utils.testing import simple_pod

from kama_sdk.core.core.config_man import config_man
from kama_sdk.model.base.common import RESOURCE_SELECTOR_KEY
from kama_sdk.model.supplier.base import supplier
from kama_sdk.model.supplier.base.supplier import OUTPUT_FMT_KEY, SERIALIZER_KEY, IS_MANY_KEY
from kama_sdk.model.supplier.ext.biz.resources_supplier import ResourcesSupplier
from kama_sdk.utils.unittest.base_classes import ClusterTest


class TestResourcesSupplier(ClusterTest):

  def test_options_format_native_ser(self):
    simple_pod.create(name='p1', ns=config_man.get_ns())
    simple_pod.create(name='p2', ns=config_man.get_ns())

    inst = ResourcesSupplier({
      SERIALIZER_KEY: supplier.SER_NATIVE,
      OUTPUT_FMT_KEY: 'options_format',
      RESOURCE_SELECTOR_KEY: 'expr::Pod:*',
      IS_MANY_KEY: False,
    })

    result = inst.resolve()
    self.assertEqual({'id': 'p1', 'title': 'p1'},  result)

  def test_jq_query(self):
    query = '.[].status.node_info.container_runtime_version'
    inst = ResourcesSupplier({
      OUTPUT_FMT_KEY: query,
      RESOURCE_SELECTOR_KEY: 'expr::nodes:*'
    })
    actual: str = inst.resolve()
    self.assertTrue(actual.startswith('containerd'))

  def test_produce_str_native_ser(self):
    simple_pod.create(name='p1', ns=config_man.get_ns())

    inst = ResourcesSupplier({
      OUTPUT_FMT_KEY: 'raw.status.phase',
      RESOURCE_SELECTOR_KEY: 'expr::Pod:*',
      IS_MANY_KEY: True,
      SERIALIZER_KEY: supplier.SER_NATIVE
    })

    result = inst.resolve()
    self.assertEqual(["Pending"], result)

  def test_produce_str_native_ser_two(self):
    simple_pod.create(name='p1', ns=config_man.get_ns())

    inst = ResourcesSupplier({
      OUTPUT_FMT_KEY: 'ternary_status',
      RESOURCE_SELECTOR_KEY: 'expr::Pod:*',
      supplier.IS_MANY_KEY: False,
      supplier.SERIALIZER_KEY: supplier.SER_NATIVE
    })

    result = inst.resolve()
    self.assertEqual("pending", result)
