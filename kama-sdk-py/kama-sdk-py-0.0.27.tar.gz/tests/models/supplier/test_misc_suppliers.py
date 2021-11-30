from kama_sdk.model.base.common import PREDICATE_KEY
from kama_sdk.model.base.mc import KIND_KEY, ID_KEY
from kama_sdk.model.base.models_manager import models_manager
from kama_sdk.model.predicate.common_predicates import TruePredicate
from kama_sdk.model.predicate.predicate import CHECK_AGAINST_KEY, OPERATOR_KEY
from kama_sdk.model.supplier.base.misc_suppliers import ListFlattener, \
  ListPluck, ListFilterSupplier, MergeSupplier, \
  UnsetSupplier
from kama_sdk.model.supplier.base.supplier import Supplier, SRC_DATA_KEY
from kama_sdk.utils.unittest.base_classes import ClusterTest


class TestListFilter(ClusterTest):
  def test_compute(self):
    inst = ListFilterSupplier({
      SRC_DATA_KEY: [1, 2, 3],
      PREDICATE_KEY: {
        CHECK_AGAINST_KEY: 1,
        OPERATOR_KEY: '>'
      }
    })

    self.assertEqual([2, 3], inst.resolve())


class TestListFlattener(ClusterTest):

  def test_resolve(self):
    inst = ListFlattener({
      'pointer': ['pt-one', 'pt-two'],
      SRC_DATA_KEY: [
        'get::self>>pointer',
        ['local-list-item'],
        'local-scalar'
      ]
    })

    expected = ['pt-one', 'pt-two', 'local-list-item', 'local-scalar']
    self.assertEqual(expected, inst.resolve())


class TestListPluckSupplier(ClusterTest):

  def test_resolve(self):
    inst = ListPluck({
      SRC_DATA_KEY: [
        {'include': False, 'value': 'unexpected'},
        {'include': True, 'value': 'expected'},
        {'include': TruePredicate.__name__, 'value': 'also-expected'}
      ]
    })

    expect = ['expected', 'also-expected']
    self.assertEqual(expect, inst.resolve())

  def test_resolve_flat(self):
    inst = ListPluck({
      'flat': True,
      SRC_DATA_KEY: [
        {'include': True, 'value': ['one', 'two']},
        {'include': TruePredicate.__name__, 'value': ['three']}
      ]
    })

    expect = ['one', 'two', 'three']
    self.assertEqual(expect, inst.resolve())


class TestMergeSupplier(ClusterTest):

  def test_compute(self):
    models_manager.add_any_descriptors([merge_test_child_desc])

    supplier_desc = {SRC_DATA_KEY: ['get::child-one', {'bar': 'baz'}]}
    inst = MergeSupplier(supplier_desc)

    actual = inst.resolve()
    expected = {'foo': 'bar', 'bar': 'baz'}
    self.assertEqual(expected, actual)


class TestUnsetSupplier(ClusterTest):
  def test_compute(self):
    model: UnsetSupplier = UnsetSupplier.inflate({
      'victim_keys': ['x'],
      SRC_DATA_KEY: {'x': 'x', 'y': 'y'}
    })
    self.assertEqual({'y': 'y'}, model.resolve())


merge_test_child_desc = {
  KIND_KEY: Supplier.__name__,
  ID_KEY: 'child-one',
  SRC_DATA_KEY: {'foo': 'bar'}
}
