from kama_sdk.model.base import mc
from kama_sdk.model.base.model import Model
from kama_sdk.model.supplier.base import supplier as sup
from kama_sdk.model.supplier.base.supplier import Supplier
from kama_sdk.utils.unittest.base_classes import KamaTest

kind = mc.KIND_KEY
idk = mc.ID_KEY
source = sup.SRC_DATA_KEY
mod_str = Model.__name__
sup_str = Supplier.__name__
depth = mc.DEPTH_KW
attr = mc.ATTR_KW


class TestModelAttrResolutionIntegration(KamaTest):

  def test_get_attr_flat_double_ref(self):
    inst = Model.inflate(double_ref)
    self.assertEqual("x", inst.get_attr("x"))
    self.assertEqual("x", inst.get_attr("x_ref"))
    self.assertEqual("x", inst.get_attr("x_ref_ref"))

  def test_get_attr_nested_double_ref(self):
    parent = Model.inflate(double_ref_with_nesting)
    child = parent.inflate_child(Model, **{attr: 'child'})
    self.assertEqual("x", child.get_attr("l2_parent_x_ref"))
    self.assertEqual("x", child.get_attr("l2_parent_x_ref_ref"))
    self.assertEqual("x", child.get_attr("l2_l2_x_ref_ref"))
    self.assertEqual("x", child.get_attr("l2_l2_x_ref_ref2"))

  def test_jq_sugar_on_attr(self):
    inst = Model({'x': {'y': 'z', 'l': [1, 2, 3]}})
    actual = inst.resolve_attr_value("get::self>>x->.y")
    self.assertEqual("z", actual)
    actual = inst.resolve_attr_value("get::self>>x->.l | length")
    self.assertEqual(3, actual)


double_ref = {
  'x': 'x',
  'x_ref': "get::self>>x",
  'x_ref_ref': "get::self>>x_ref"
}


double_ref_with_nesting = {
  'x': 'x',
  'x_ref': "get::self>>x",
  'child': {
    kind: Model.__name__,
    'l2_parent_x_ref': 'get::self>>x',
    'l2_parent_x_ref_ref': "get::self>>x_ref",
    'l2_l2_x_ref_ref': "get::self>>l2_parent_x_ref",
    'l2_l2_x_ref_ref2': "get::self>>l2_parent_x_ref_ref",
  }
}
