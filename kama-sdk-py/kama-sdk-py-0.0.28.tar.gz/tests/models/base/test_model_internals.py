from kama_sdk.model.base.mc import CACHE_SPEC_KEY, KIND_KEY
from kama_sdk.model.base.model import Model
from kama_sdk.model.base.model_decorators import model_attr
from kama_sdk.utils.unittest.base_classes import ClusterTest


class TestModelInternals(ClusterTest):

  def test_get_virtual_attr_defs_exactly(self):
    actual = DecoratedModel({}).get_virtual_attr_defs()
    self.assertEqual(virtual_attr_exp, actual)

  def test_not_cached_virtual_attr(self):
    inst = DecoratedModel(cached_and_not_desc)
    inst.cache_attr_resolution_result("no_cache", "illegally cached")
    actual = inst.get_attr("resolved_no_cache")
    self.assertEqual("no_cache", actual)

  def test_get_all_cacheable_attr_keys(self):
    inst = DecoratedModel(cached_and_not_desc)
    actual = inst.get_cacheable_attr_keys()
    self.assertEqual(sorted(virtual_attr_keys_exp), sorted(actual))

  def test_descriptor_pointer_release(self):
    descriptor = {'foo': 'bar'}
    inst = Model(descriptor)
    descriptor['foo'] = 'baz'
    self.assertEqual('bar', inst.get_config().get('foo'))

  def test_get_attr_normal_resolution(self):
    inst = Model({'foo': 'bar'})
    self.assertEqual("bar", inst.get_attr('foo'))

  def test_get_virtual_attr_with_name_override(self):
    inst = DecoratedModel.inflate({})
    actual = inst.get_attr("named")
    self.assertEqual("named", actual)

  def test_get_cached_attr(self):
    inst = Model.inflate(cached_and_not_desc)
    self.assertEqual({}, inst.get_results_cache())
    actual = inst.get_attr("y")
    self.assertEqual("y", actual)
    self.assertEqual({'y': 'y'}, inst.get_results_cache())

  def test_multi_generation_cache(self):
    """
    Ensure that if a child calls a supplier that a parent caches,
    the parent's cache reacts.
    :return:
    """
    parent = Model.inflate(multi_gen_cache_desc)
    child = parent.inflate_child(Model, attr="child")
    self.assertEqual({}, parent.get_results_cache())
    self.assertEqual({}, child.get_results_cache())
    self.assertEqual("x", child.get_attr("x"))
    self.assertEqual({"x": "x"}, parent.get_results_cache())
    self.assertEqual({}, child.get_results_cache())

  def test_cache_attr_resolution_result(self):
    inst = Model.inflate(cached_and_not_desc)
    self.assertEqual({}, inst.get_results_cache())
    inst.cache_attr_resolution_result('x', 'x!')
    inst.cache_attr_resolution_result('y', 'y!')
    self.assertEqual({'y': 'y!'}, inst.get_results_cache())

  def test_cache_intercept_for_normal_method_call(self):
    """
    Ensure that the caching mechanism kicks in not only when
    an attr is requested, but also for normal instance method calls,
    i.e my_model.get_expensive_thing()
    :return:
    """
    inst = DecoratedModel({})
    self.assertNotEqual(inst.control(), inst.control())
    self.assertEqual(inst.pointer(), inst.pointer())

  def test_cache_direct_invoke_vs_get_attr_cache_sharing(self):
    """
    Ensure that the caching mechanism kicks in not only when
    an attr is requested, but also for normal instance method calls,
    i.e my_model.get_expensive_thing()
    :return:
    """
    inst = DecoratedModel({})
    self.assertEqual(inst.pointer(), inst.get_attr("resolved_pointer"))

    inst = DecoratedModel({})
    self.assertEqual(inst.get_attr("resolved_pointer"), inst.pointer())

  def test_cache_does_not_spill_to_siblings_direct_invokation(self):
    """
    Make sure that a `Model` instance register decorators with itself rather
    than spilling over to siblings.
    :return:
    """
    inst_one = PrivateModel({'my_own': 'x'})
    inst_two = PrivateModel({'my_own': 'y'})
    self.assertEqual('x', inst_one.get_my_own())
    self.assertEqual('y', inst_two.get_my_own())

  def test_cache_does_not_spill_to_siblings_attr_invokation(self):
    """
    Make sure that a `Model` instance register decorators with itself rather
    than spilling over to siblings.
    :return:
    """
    inst_one = PrivateModel({'my_own': 'x'})
    inst_two = PrivateModel({'my_own': 'y'})
    self.assertEqual('x', inst_one.get_local_attr("my_own"))
    self.assertEqual('y', inst_two.get_local_attr("my_own"))


# noinspection PyMethodMayBeStatic
class DecoratedModel(Model):
  def normal_instance_method(self):
    pass

  @model_attr(key='named')
  def named(self):
    return 'named'

  @model_attr(cached=False)
  def no_cache(self):
    return 'no_cache'

  @model_attr()
  def naked(self):
    return 'naked'

  @model_attr(cached=True)
  def pointer(self):
    return object()

  def control(self):
    return object()


class PrivateModel(Model):
  @model_attr(key='my_own')
  def get_my_own(self):
    return self.get_config()['my_own']


multi_gen_cache_desc = {
  CACHE_SPEC_KEY: {
    'x': 'x'
  },
  'child': {
    KIND_KEY: Model.__name__
  }
}


cached_and_not_desc = {
  'x':  'x',
  CACHE_SPEC_KEY: {
    'y': 'y'
  }
}


virtual_attr_exp = [
  {'func_name': 'naked', 'attr_name': 'resolved_naked', 'should_cache': False},
  {'func_name': 'named', 'attr_name': 'named', 'should_cache': False},
  {'func_name': 'no_cache', 'attr_name': 'resolved_no_cache', 'should_cache': False},
  {'attr_name': 'resolved_pointer', 'func_name': 'pointer', 'should_cache': True}
]


virtual_attr_keys_exp = ['resolved_pointer', 'y']