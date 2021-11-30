from typing import Any

from kama_sdk.model.base import mc, model
from kama_sdk.model.base.model import Model
from kama_sdk.model.base.models_manager import models_manager
from kama_sdk.model.supplier.base import supplier as sup
from kama_sdk.model.supplier.base.supplier import Supplier
from kama_sdk.utils.unittest.base_classes import KamaTest

kind = mc.KIND_KEY
idk = mc.ID_KEY
data = sup.SRC_DATA_KEY
attr = mc.ATTR_KW
safely = mc.INFLATE_SAFELY_KW


class TestModelAssociations(KamaTest):

  def test_inflate_child_with_none(self):
    self._test_inflate_child_with_none(None)

  def test_inflate_child_with_bad_ref(self):
    self._test_inflate_child_with_none(None)

  def test_inflate_child_with_non_kod(self):
    self._test_inflate_child_with_none(['not-a-kod'])
    self._test_inflate_child_with_none(1)

  def test_inflate_child_with_lookup_with_inline_desc(self):
    child_descriptor = {kind: Model.__name__, idk: 'child-id'}
    parent = Model.inflate({'child': child_descriptor})
    child = parent.inflate_child(Model, **{mc.ATTR_KW: 'child'})
    self.assertEqual(Model, type(child))
    self.assertEqual('child-id', child.get_id())

  def test_inflate_child_with_lookup_with_id_ref(self):
    child_descriptor = {kind: Model.__name__, idk: 'child-id'}
    models_manager.add_descriptors([child_descriptor])
    parent = Model.inflate({'child': "id::child-id"})
    child = parent.inflate_child(Model, **{mc.ATTR_KW: 'child'})
    self.assertEqual(Model, type(child))
    self.assertEqual('child-id', child.get_id())

  def test_inflate_child_no_lookup_with_inline_desc(self):
    child_descriptor = {kind: Model.__name__, idk: 'child-id'}
    parent = Model.inflate({})
    child = parent.inflate_child(Model, kod=child_descriptor)
    self.assertEqual(Model, type(child))
    self.assertEqual('child-id', child.get_id())

  def test_inflate_child_no_lookup_with_id_ref(self):
    child_descriptor = {kind: Model.__name__, idk: 'child-id'}
    models_manager.add_descriptors([child_descriptor])
    parent = Model.inflate({})
    child = parent.inflate_child(Model, **{mc.KOD_KW: "id::child-id"})
    self.assertEqual(Model, type(child))
    self.assertEqual('child-id', child.get_id())

  def test_inflate_non_supplier_preceded_by_suppliers(self):
    inst = Model.inflate(non_supplier_preceded_by_suppliers)
    child = inst.inflate_child(Model, attr=CHILD_KEY)
    self.assertEqual(Model, type(child))
    self.assertEqual('nested-non-supplier', child.get_id())

  def test_inflate_lazy_supplier_preceded_by_suppliers(self):
    inst = Model.inflate(lazy_supplier_preceded_by_suppliers)
    child = inst.inflate_child(Model, **{mc.ATTR_KW: CHILD_KEY})
    self.assertEqual(Supplier, type(child))
    self.assertEqual('nested-lazy-supplier', child.get_id())

  def test_inflate_eager_supplier_incorrectly_preceded_by_suppliers(self):
    """
    If leaf model is an eager Supplier, the final inflatable value will
    be the supplier's resolve(), instead of its KoD. This test ensures
    that inflate_child returns None in this case (if safely=True is passed).
    :return:
    """
    inst = Model.inflate(eager_supplier_preceded_by_suppliers)
    kwargs = {mc.ATTR_KW: CHILD_KEY, mc.INFLATE_SAFELY_KW: True}
    child = inst.inflate_child(Model, **kwargs)
    self.assertEqual(None, child)

  def _test_inflate_child_with_none(self, val: Any):
    parent = Model.inflate({'child': val})

    with self.assertRaises(model.InflateError):
      parent.inflate_child(Model, **{attr: 'child'})

    child = parent.inflate_child(Model, **{attr: 'child', safely: True})
    self.assertIsNone(child)

  # def test_inflate_child_with_prop(self):
  #   instance = LabRat({
  #     'child':  {
  #       mc.KIND_KEY: ChildClass.__name__,
  #       mc.TITLE_KEY: "foo"
  #     }
  #   })
  #   child_instance = instance.inflate_child(ChildClass, attr='child')
  #   self.assertEqual(ChildClass.__name__, child_instance.kind())
  #   self.assertEqual(ChildClass, type(child_instance))
  #   self.assertEqual("foo", child_instance.get_title())
  #
  # def test_inflate_child_with_kod(self):
  #   instance = LabRat({})
  #   child_instance = instance.inflate_child(ChildClass, kod={
  #     mc.KIND_KEY: ChildClass.__name__,
  #     mc.TITLE_KEY: "foo"
  #   })
  #   # print(child_instance)
  #
  #   self.assertEqual(ChildClass.__name__, child_instance.kind())
  #   self.assertEqual(ChildClass, child_instance.__class__)
  #   self.assertEqual("foo", child_instance.get_title())
  #
  # def test_inflate_child_with_supplier(self):
  #   models_manager.add_models([ChildClass])
  #
  #   instance = LabRat({
  #     'child': {
  #       mc.KIND_KEY: Switch.__name__,
  #       supplier.SRC_DATA_KEY: [
  #         {
  #           'break': True,
  #           'value': {
  #             mc.KIND_KEY: ChildClass.__name__,
  #             mc.ID_KEY: 'right-child'
  #           }
  #         },
  #         {
  #           'break': False,
  #           'value': {
  #             mc.KIND_KEY: ChildClass.__name__,
  #             mc.ID_KEY: 'wrong-child'
  #           }
  #         }
  #       ]
  #     }
  #   })
  #   child = instance.inflate_child(ChildClass, attr='child')
  #   self.assertEqual('right-child', child.get_id())
  #
  # def test_inflate_children_with_query(self):
  #   models_manager.add_models([ChildClass])
  #   models_manager.add_any_descriptors([
  #     {
  #       mc.KIND_KEY: ChildClass.__name__,
  #       mc.ID_KEY: 'child-one'
  #     },
  #     {
  #       mc.KIND_KEY: ChildClass.__name__,
  #       mc.ID_KEY: 'child-two'
  #     }
  #   ])
  #
  #   instance = LabRat({'children': {mc.ID_KEY: 'child-one'}})
  #   result = instance.inflate_children(ChildClass, attr='children')
  #
  #   self.assertEqual(1, len(result))
  #   self.assertEqual('child-one', result[0].get_id())
  #
  # def test_inflate_children_with_supplier(self):
  #   models_manager.add_models([ChildClass])
  #
  #   instance = LabRat({
  #     'children': {
  #       mc.KIND_KEY: Supplier.__name__,
  #       supplier.SRC_DATA_KEY: [
  #         {mc.KIND_KEY: ChildClass.__name__, mc.ID_KEY: 'child-one'},
  #         {mc.KIND_KEY: ChildClass.__name__, mc.ID_KEY: 'child-two'}
  #       ]
  #     }
  #   })
  #
  #   children = instance.inflate_children(ChildClass, attr='children')
  #   self.assertEqual(2, len(children))
  #   self.assertEqual('child-one', children[0].get_id())
  #   self.assertEqual('child-two', children[1].get_id())
  #
  # def test_inflate_children(self):
  #   models_manager.add_any_descriptors([
  #     {
  #       mc.ID_KEY: 'independent-child',
  #       mc.KIND_KEY: ChildClass.__name__
  #     },
  #     {
  #       mc.ID_KEY: 'non-child',
  #       mc.KIND_KEY: ChildClass.__name__
  #     },
  #     {
  #       mc.ID_KEY: 'parent',
  #       mc.KIND_KEY: LabRat.__name__,
  #       'children': [
  #         'independent-child',
  #         {
  #           mc.KIND_KEY: ChildClass.__name__,
  #           mc.ID_KEY: 'embedded-child'
  #         }
  #       ]
  #     }
  #   ])
  #
  #   models_manager.add_models([ChildClass])
  #   parent_inst = LabRat.inflate('parent')
  #   sig = lambda inst: {mc.ID_KEY: inst.get_id(), 'cls': inst.__class__}
  #   result = parent_inst.inflate_children(ChildClass, attr='children')
  #   exp = [
  #     {mc.ID_KEY: 'independent-child', 'cls': ChildClass},
  #     {mc.ID_KEY: 'embedded-child', 'cls': ChildClass}
  #   ]
  #   self.assertEqual(exp, list(map(sig, result)))
  #

class LabRat(Model):
  pass


class ChildClass(Model):
  pass


CHILD_KEY = 'child'


non_supplier_preceded_by_suppliers = {
  CHILD_KEY: {
    mc.KIND_KEY: Supplier.__name__,
    sup.SRC_DATA_KEY: {
      mc.KIND_KEY: Supplier.__name__,
      sup.SRC_DATA_KEY: {
        mc.KIND_KEY: Model.__name__,
        mc.ID_KEY: "nested-non-supplier"
      }
    }
  }
}


lazy_supplier_preceded_by_suppliers = {
  CHILD_KEY: {
    mc.KIND_KEY: Supplier.__name__,
    sup.SRC_DATA_KEY: {
      mc.KIND_KEY: Supplier.__name__,
      sup.SRC_DATA_KEY: {
        mc.KIND_KEY: Supplier.__name__,
        mc.ID_KEY: "nested-lazy-supplier",
        mc.LAZY_KEY: True
      }
    }
  }
}


eager_supplier_preceded_by_suppliers = {
  CHILD_KEY: {
    mc.KIND_KEY: Supplier.__name__,
    sup.SRC_DATA_KEY: {
      mc.KIND_KEY: Supplier.__name__,
      sup.SRC_DATA_KEY: {
        mc.KIND_KEY: Supplier.__name__
      }
    }
  }
}

