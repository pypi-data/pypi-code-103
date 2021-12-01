from typing import Dict

from kama_sdk.model.base import mc
from kama_sdk.model.base.model import Model
from kama_sdk.model.supplier.base import supplier as sp, supplier
from kama_sdk.model.supplier.base.supplier import Supplier
from kama_sdk.utils.unittest.base_classes import KamaTest

kind = mc.KIND_KEY
idk = mc.ID_KEY
source = sp.SRC_DATA_KEY
output = sp.OUTPUT_FMT_KEY
mod_str = Model.__name__
sup_str = Supplier.__name__
depth = mc.DEPTH_KW
attr = mc.ATTR_KW
many = sp.IS_MANY_KEY


class TestSupplier(KamaTest):

  def test_serialize_jq(self):
    instance = jq_supplier({output: '.foo'})
    result = instance.do_jq_serialize({'foo': 'bar'})
    self.assertEqual('bar', result)

    instance = jq_supplier({})
    result = instance.do_jq_serialize({'foo': 'bar'})
    self.assertEqual(dict(foo='bar'), result)

    instance = jq_supplier({output: '.no-effect'})
    result = instance.do_jq_serialize(None)
    self.assertEqual(None, result)

    instance = jq_supplier({output: '. | length'})
    result = instance.do_jq_serialize(['foo', 'bar'])
    self.assertEqual(2, result)

    instance = jq_supplier({output: '.[].foo'})
    result = instance.do_jq_serialize([{'foo': 'bar'}])
    self.assertEqual('bar', result)

    instance = jq_supplier({output: '.[].foo', many: True})
    result = instance.do_jq_serialize([{'foo': 'bar'}])
    self.assertEqual(['bar'], result)

  def test_serialize_item_prop_default(self):
    result = Supplier.serialize_item_prop('foo', None)
    self.assertEqual('foo', result)

    result = Supplier.serialize_item_prop('foo', 'bar')
    self.assertEqual(None, result)

    result = Supplier.serialize_item_prop({'foo': 'bar'}, 'foo')
    self.assertEqual('bar', result)

    result = Supplier.serialize_item_prop('foo', 'lower')
    self.assertEqual('foo', result)

  def test_serialize_item_prop_len(self):
    result = Supplier.serialize_item_prop(None, '__count__')
    self.assertEqual(0, result)

    result = Supplier.serialize_item_prop('abc', '__count__')
    self.assertEqual(3, result)

    result = Supplier.serialize_item_prop(['a'], '__count__')
    self.assertEqual(1, result)

  def test_serialize_item_default(self):
    instance = native_supplier(dict())
    result = instance.serialize_item('Letter')
    self.assertEqual('Letter', result)

  def test_serialize_item_blank(self):
    instance = native_supplier(dict(output=''))
    result = instance.serialize_item('Letter')
    self.assertEqual('Letter', result)

  def test_serialize_item_string(self):
    instance = native_supplier(dict(output='lower'))
    result = instance.serialize_item('Letter')
    self.assertEqual('letter', result)

  def test_serialize_item_dict(self):
    instance = native_supplier({output: {'lower_case': 'lower'}})
    result = instance.serialize_item('Letter')
    self.assertEqual({'lower_case': 'letter'}, result)

  def test_serialize_item_dict_identity(self):
    instance = native_supplier({output: {'x': sp.NATIVE_IDENTITY_TOK}})
    result = instance.serialize_item({'y': 'z'})
    self.assertEqual({'x': {'y': 'z'}}, result)

  def test_serialize_item_deep_dict(self):
    instance = native_supplier({output: 'one.two'})
    result = instance.serialize_item({'one': {'two': 'three'}})
    self.assertEqual('three', result)

  def test_serialize_item_deep_dict2(self):
    instance = native_supplier({output: 'one'})
    result = instance.serialize_item({'one': {'two': 'three'}})
    self.assertEqual({'two': 'three'}, result)

  def test_serialize_item_deep_dict3(self):
    instance = native_supplier({output: ''})
    result = instance.serialize_item({'one': {'two': 'three'}})
    self.assertEqual({'one': {'two': 'three'}}, result)

  def test_serialize_item_deep_dict4(self):
    instance = native_supplier({})
    result = instance.serialize_item({'one': {'two': 'three'}})
    self.assertEqual({'one': {'two': 'three'}}, result)

  def test_serialize_python_prop(self):
    instance = native_supplier({output: "foo_prop"})
    result = instance.serialize_item(Obj())
    self.assertEqual('foo', result)

  def test_serialize_python_method(self):
    instance = native_supplier({output: "bar_method"})
    result = instance.serialize_item(Obj())
    self.assertEqual('bar', result)

  def test_serialize_from_model(self):
    instance = native_supplier({output: "milk?"})
    result = instance.serialize_item(Obj())
    self.assertEqual('got-milk?', result)

  def test_serialize_explicit_many(self):
    instance = native_supplier({many: True})
    result = instance.do_native_serialize('Letter')
    self.assertEqual(['Letter'], result)

    instance = native_supplier({many: False, output: 'foo'})
    _input = [dict(foo='bar'), dict(foo='rab')]
    result = instance.do_native_serialize(_input)
    self.assertEqual('bar', result)

  def test_serialize_item_dict_identity_many(self):
    params = {many: True, output: {'x': sp.NATIVE_IDENTITY_TOK}}
    instance = native_supplier(params)
    result = instance.do_native_serialize({'y': 'z'})
    self.assertEqual([{'x': {'y': 'z'}}], result)

    instance = native_supplier({output: {'x': sp.NATIVE_IDENTITY_TOK}})
    result = instance.do_native_serialize([{'y': 'z'}])
    self.assertEqual([{'x': {'y': 'z'}}], result)

  def test_serialize_explicit_auto(self):
    instance = native_supplier({})
    result = instance.do_native_serialize([dict(foo='bar')])
    self.assertEqual([dict(foo='bar')], result)

    instance = native_supplier({output: {'Bar': 'bar'}})
    result = instance.do_native_serialize({'foo': 'bar', 'bar': 'baz'})
    self.assertEqual({'Bar': 'baz'}, result)

  # def test_serialize_explicit_transform(self):
  #   instance = ValueSupplier({'bytes': 'auto_unit'})
  #   result = instance.serialize_computed_value([{'bytes': 1000}])
  #   self.assertEqual([{'bytes': 1}], result)

def jq_supplier(config: Dict):
  return Supplier({**config, supplier.SERIALIZER_KEY: supplier.SER_JQ})


def native_supplier(config):
  return Supplier({**config, supplier.SERIALIZER_KEY: supplier.SER_NATIVE})


class Obj:
  @property
  def foo_prop(self):
    return 'foo'

  # noinspection PyMethodMayBeStatic
  def bar_method(self):
    return 'bar'

  # noinspection PyMethodMayBeStatic
  def get_prop(self, prop_key):
    return f"got-{prop_key}"
