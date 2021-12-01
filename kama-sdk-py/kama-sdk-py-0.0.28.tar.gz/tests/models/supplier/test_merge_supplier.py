from kama_sdk.model.base.mc import KIND_KEY
from kama_sdk.model.supplier.base.misc_suppliers import MergeSupplier
from kama_sdk.model.supplier.base.supplier import SRC_DATA_KEY
from kama_sdk.utils.unittest.base_classes import KamaTest


class TestMergeSupplier(KamaTest):

  def test_resolve(self):
    inst = MergeSupplier.inflate(descriptor)
    actual = inst.resolve()
    expect = {'a': {'e': 'g', 'b': 'd'}}
    self.assertEqual(expect, actual)


descriptor = {
  KIND_KEY: MergeSupplier.__name__,
  'f': 'g',
  SRC_DATA_KEY: [
    None,
    {'a': {'b': 'c'}},
    {'a': {'b': 'd'}},
    {'a': {'e': "get::self>>f"}}
  ]
}
