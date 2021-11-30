from kama_sdk.model.base.mc import KIND_KEY, ID_KEY, ATTR_KW, FORCE_INFLATE_PREFIX
from kama_sdk.model.base.model import Model
from kama_sdk.model.base.models_manager import models_manager
from kama_sdk.model.supplier.base.supplier import Supplier, SRC_DATA_KEY
from kama_sdk.model.predicate.common_predicates import TruePredicate
from kama_sdk.utils.unittest.base_classes import KamaTest


sup_str = Supplier.__name__


class TestModelValueResolution(KamaTest):

  def test_supplier_resolve_or_identity_with_non_supplier_model_desc(self):
    """
    Ensure interceptor does not intercept a non-Supplier Model descriptor
    """
    inst = Model.inflate({})
    unresolved = {KIND_KEY: Model.__name__}
    resolved = inst.supplier_resolve_or_identity(unresolved)
    self.assertEqual(unresolved, resolved)

  def test_supplier_resolve_or_identity_with_bad_get_id(self):
    """
    Ensure the Model's supply-interceptor returns None instead
    of crashing if get::<id> is passed with a bad id.
    """
    resolved = Model({}).supplier_resolve_or_identity("get::dne")
    self.assertEqual(None, resolved)

  def test_supplier_resolve_or_identity_with_supplier_model_desc(self):
    """
    Ensure interceptor intercepts and resolves a Supplier descriptor
    """
    unresolved = {KIND_KEY: sup_str, SRC_DATA_KEY: '1'}
    resolved = Model({}).supplier_resolve_or_identity(unresolved)
    self.assertEqual("1", resolved)

  def test_supplier_resolve_or_identity_with_supplier_model_id(self):
    """
    Ensure interceptor intercepts and resolves a valid Supplier id
    """
    desc = {ID_KEY: "x", KIND_KEY: sup_str, SRC_DATA_KEY: '1'}
    models_manager.add_descriptors([desc])
    resolved = Model({}).supplier_resolve_or_identity("get::x")
    self.assertEqual("1", resolved)

  def test_resolve_dict_attr_value_with_simple_supplier(self):
    sup_desc = {KIND_KEY: sup_str, SRC_DATA_KEY: 'simple'}
    resolved = Model({}).resolve_attr_value(sup_desc)
    self.assertEqual('simple', resolved)

  def test_resolve_str_attr_value_with_supplier_ref(self):
    sup_desc = {ID_KEY: 'sup', KIND_KEY: sup_str, SRC_DATA_KEY: 'simple'}
    models_manager.add_descriptors([sup_desc])
    resolved = Model({}).resolve_attr_value("get::sup")
    self.assertEqual('simple', resolved)

  def test_resolve_str_attr_value_with_sugar_id_supplier_expr_delayed(self):
    models_manager.add_descriptors([{KIND_KEY: Model.__name__, ID_KEY: 'help'}])
    resolved = Model({}).resolve_attr_value("get::&id::help")
    self.assertEqual(Model, type(resolved))
    self.assertEqual("help", resolved.get_id())

  def test_resolve_str_attr_value_with_sugar_expr_supplier_expr_delayed(self):
    expr = f"get::&KIND_KEY::{TruePredicate.__name__}"
    resolved = Model({}).resolve_attr_value(expr)
    self.assertEqual(TruePredicate, type(resolved))

  def test_resolve_str_attr_value_with_sugar_expr_supplier_expr(self):
    models_manager.add_models([FooSupplier])
    sugar_expr = f"get::KIND_KEY::{FooSupplier.__name__}"
    self.assertEqual("foo", Model({}).resolve_attr_value(sugar_expr))

  def test_resolve_str_attr_value_with_sugar_supplier_expr_ser_attr(self):
    helper_descriptor = {KIND_KEY: Model.__name__, ID_KEY: 'help'}
    models_manager.add_descriptors([helper_descriptor])
    resolved = Model({}).resolve_attr_value("get::&id::help>>id")
    self.assertEqual('help', resolved)

  def test_resolve_str_attr_value_with_sugar_supplier_expr_ser_jq(self):
    helper_descriptor = {KIND_KEY: Model.__name__, ID_KEY: 'help', 'x': {'y': 'z'}}
    models_manager.add_descriptors([helper_descriptor])
    resolved = Model({}).resolve_attr_value("get::&id::help>>x->.y")
    self.assertEqual('z', resolved)

  def test_resolve_str_attr_value_with_sugar_supplier_self_expr(self):
    resolved = Model({'x': 'y'}).resolve_attr_value("get::self>>x")
    self.assertEqual('y', resolved)

  def test_resolve_str_attr_value_with_sugar_supplier_parent_expr(self):
    parent = Model.inflate(many_parents)
    child = parent.inflate_child(Model, **{ATTR_KW: 'child'})
    baby = child.inflate_child(Model, **{ATTR_KW: 'child'})
    self.assertEqual("x!", baby.resolve_attr_value("get::parent>>x"))

  def test_interpolate_str_attr_value(self):
    inst = Model({'x': 'x', 'y': "foo ${get::self>>x}"})
    self.assertEqual("foo x", inst.get_attr("y"))

  def test_resolve_dict_attr_value_depth_zero(self):
    """
    Ensure interceptor does not intercept a non-descriptor Dict
    """
    inst = Model.inflate(multi_test_desc)
    self.assertEqual({'b': 'get::self>>a'}, inst.get_attr('b'))

  def test_resolve_dict_attr_value_depth_ten(self):
    """
    Ensure interceptor does not intercept a non-descriptor Dict
    """
    inst = Model.inflate(multi_test_desc)
    self.assertEqual({'b': 'a'}, inst.get_attr('b', depth=10))

  def test_resolve_list_attr_value_with_flat_inputs(self):
    """
    Ensure that individual list items work with the resolution
    pipeline.
    :return:
    """
    inst = Model.inflate(multi_test_desc)
    self.assertEqual(["c", "a"], inst.get_attr("c"))

  def test_resolve_list_attr_value_with_deep_inputs_depth_zero(self):
    """
    Ensure that when depth = 0 is passed when getting a list, any
    items that are dict DO NOT go through the resolution pipeline.
    :return:
    """
    inst = Model.inflate(multi_test_desc)
    expect = ['d', {'x': 'get::self>>a'}]
    self.assertEqual(expect, inst.get_attr('d'))

  def test_resolve_list_attr_value_with_deep_inputs_depth_ten(self):
    """
    Ensure that when depth > 0 is passed when getting a list, any
    items that are dict go through the resolution pipeline.
    :return:
    """
    inst = Model.inflate(multi_test_desc)
    actual = inst.get_attr('d', depth=10)
    expect = ['d', {'x': 'a'}]
    self.assertEqual(expect, actual)

  def test_resolve_list_attr_value_with_splatter_flat_items(self):
    """
    Ensure that when depth > 0 is passed when getting a list, any
    items that are dict go through the resolution pipeline.
    :return:
    """
    inst = Model.inflate(multi_test_desc)
    actual = inst.get_attr('e')
    expect = ['e', 'c', 'a']
    self.assertEqual(expect, actual)

  def test_resolve_list_attr_value_with_nested_splatter(self):
    inst = Model.inflate(multi_test_desc)
    actual = inst.get_attr('f')
    expect = ['f', 'e', 'c', 'a']
    self.assertEqual(expect, actual)

  def test_resolve_list_attr_value_with_splattered_deep_dict(self):
    inst = Model.inflate(multi_test_desc)
    actual = inst.get_attr('g', depth=10)
    print(actual)
    # TODO this does not work because when resolve_str_attr_value creates
    # TODO a new supplier that does not pass the **kwargs (so depth=10 is list)
    # expect = ['g', 'd', {'x': 'a'}]
    # self.assertEqual(expect, actual)

  def test_force_inflate(self):
    models_manager.add_descriptors([referenced_child])
    inst = Model.inflate(generic_children_parent)
    child_one = inst.get_attr("child-one")
    child_two = inst.get_attr("child-two")
    self.assertEqual(Model, type(child_one))
    self.assertEqual("child-one", child_one.get_id())
    self.assertEqual(Supplier, type(child_two))
    self.assertEqual(None, child_two.get_id())


class FooSupplier(Supplier):
  def _compute(self):
    return 'foo'


multi_test_desc = {
  'a': 'a',
  'b': {'b': "get::self>>a"},
  'c': ['c', "get::self>>a"],
  'd': ["d", {"x": "get::self>>a"}],
  'e': ["e", "...get::self>>c"],
  'f': ["f", "...get::self>>e"],
  'g': ["g", "...get::self>>d"],
}


resolvable_dict_supplier = {
  KIND_KEY: Supplier.__name__,
  ID_KEY: 'dict-returner',
  'y_ref': 'y!',
  SRC_DATA_KEY: {
    'x': 'x',
    'y': "get::self>>y_ref"
  }
}


many_parents = {
  'x': 'x',
  'child':  {
    'x': 'x!',
    'child':  {
      'x': 'x!!',
    }
  }
}

referenced_child = {
  ID_KEY: 'child-one',
  KIND_KEY: Model.__name__
}

generic_children_parent = {
  ID_KEY: 'parent',
  KIND_KEY: Model.__name__,
  'child-one': f'{FORCE_INFLATE_PREFIX}id::child-one',
  'child-two': f'{FORCE_INFLATE_PREFIX}kind::{Supplier.__name__}'
}


#   def test_resolve_falsy_values(self):
#     inflated: Model = DummyModel.inflate(dict(
#       foo=None,
#       false=False,
#       null="__null__",
#       nil="__nil__",
#       zero=0,
#       empty_list=[],
#       empty_dict={}
#     ))
#
#     self.assertEqual(None, inflated.get_attr('none'))
#     self.assertEqual(None, inflated.get_attr('null'))
#     self.assertEqual(None, inflated.get_attr('nil'))
#     self.assertEqual(False, inflated.get_attr('false'))
#     self.assertEqual(0, inflated.get_attr('zero'))
#     self.assertEqual([], inflated.get_attr('empty_list'))
#     self.assertEqual({}, inflated.get_attr('empty_dict'))
#
#     self.assertEqual('backup', inflated.get_attr('none', backup='backup'))
#     self.assertEqual('backup', inflated.get_attr('missing', backup='backup'))
