from typing import Dict

from kama_sdk.model.base import attr_lookup_pipeline as pipeline, mc
from kama_sdk.model.base.attr_lookup_pipeline import AttrLookupReq
from kama_sdk.model.base.model import Model
from kama_sdk.model.base.model_decorators import model_attr
from kama_sdk.utils.unittest.base_classes import KamaTest


def mk_req(model: Model, key: str, opts: Dict):
  return AttrLookupReq(
    model=model,
    attr_key=key,
    options=opts
  )


redefine_ok = mc.REDEFINE_PREEMPT_ENABLED_FLAG
standard = mc.STANDARD_READ_ENABLED_FLAG
parent_ok = mc.PARENT_LOOKBACK_ENABLED_FLAG
virtual_ok = mc.VIRTUAL_PREEMPT_ENABLED_KEY
cache_ok = mc.CACHE_PREEMPT_ENABLED_FLAG


class TestModelAttrLookupPipeline(KamaTest):

  def test_try_preempt_with_descriptor_override_false_1(self):
    req = mk_req(Model({'x': 'x'}), 'x', {redefine_ok: False})
    result = pipeline.try_preempt_with_descriptor_override(req)
    self.assertEqual((False, None, None), result)

  def test_try_preempt_with_descriptor_override_true_1(self):
    req = mk_req(Model({'x': 'x'}), 'x', {redefine_ok: True})
    result = pipeline.try_preempt_with_descriptor_override(req)
    self.assertEqual((False, None, None), result)

  def test_try_preempt_with_descriptor_override_true_2(self):
    model = Model(redef_conf)
    req = mk_req(model, 'x', {redefine_ok: True})
    result = pipeline.try_preempt_with_descriptor_override(req)
    self.assertEqual((True, 'x!', model), result)

  def test_try_preempt_with_descriptor_override_false_2(self):
    req = mk_req(Model(redef_conf), 'x', {redefine_ok: False})
    result = pipeline.try_preempt_with_descriptor_override(req)
    self.assertEqual((False, None, None), result)

  def test_integration_redef_and_standard(self):
    inst_one = Model(desc_one)
    req = mk_req(inst_one, 'x', {redefine_ok: False})
    self.assertEqual((True, 'x', inst_one), pipeline.process(req))

    inst_two = Model(desc_one)
    req = mk_req(inst_two, 'x', {redefine_ok: True})
    self.assertEqual((True, 'x!', inst_two), pipeline.process(req))

  def test_parent_fallback_child_precedence(self):
    parent = Model.inflate(desc_four)
    child = parent.inflate_child(Model, **{mc.ATTR_KW: 'child'})
    result = pipeline.process(mk_req(child, 'x', {}))
    self.assertEqual((True, "x!", child), result)

  def test_parent_fallback_parent_precedence(self):
    """
    Ensure that when parent lookup is returned, delegate
    is in fact the parent
    :return:
    """
    parent = Model.inflate(desc_four)
    child = parent.inflate_child(Model, **{mc.ATTR_KW: 'child'})
    result = pipeline.process(mk_req(child, 'y', {}))
    self.assertEqual((True, "y", parent), result)

  def test_parent_fallback_escape(self):
    parent = Model.inflate(desc_four)
    child = parent.inflate_child(Model, **{mc.ATTR_KW: 'child'})
    result = pipeline.process(mk_req(child, 'y', {parent_ok: False}))
    self.assertEqual(False, result[0])

  def test_try_preempt_with_virtual_override(self):
    inst = VirtualAttrsModel.inflate({'x': 'x'})
    result = pipeline.process(mk_req(inst, 'x', {}))
    self.assertEqual("x!", result[1])

  def test_try_preempt_with_virtual_override_two(self):
    inst = VirtualAttrsModel.inflate({'x': 'x'})
    options = {virtual_ok: False}
    result = pipeline.process(mk_req(inst, 'x', options))
    self.assertEqual("x", result[1])

  def test_try_preempt_with_virtual_override_three(self):
    inst = VirtualAttrsModel.inflate({'x': 'x'})
    options = {virtual_ok: False, cache_ok: False}
    result = pipeline.process(mk_req(inst, 'x', options))
    self.assertEqual("x", result[1])

  # def test_try_preempt_with_virtual_override_with_cache(self):
  #   inst = VirtualAttrsModel.inflate(desc_five)
  #   result = pipeline.process(mk_req(inst, 'x', {}))
  #
  #   result = pipeline.process(mk_req(inst, 'y', {}))
  #
  #   inst.cache_attr_resolution_result('x', '7')
  #   result = pipeline.process(mk_req(inst, 'x', {}))
  #   print(result)

# def test_integration_redef_and_cache(self):
  #   req = mk_req(Model(desc_two), 'x', {})
  #   self.assertEqual((True, 'x!!'), pipeline.process(req))

    # req = mk_req(Model(desc_two), 'x', {redefine: False})
    # self.assertEqual((True, 'x'), pipeline.process(req))

    # req = mk_req(Model(desc_two), 'x', {redefine: True})
    # self.assertEqual((True, 'x!'), pipeline.process(req))

  # def test_flags(self):
    

desc_four = {
  'x': 'x',
  'y': 'y',
  'child': {
    mc.KIND_KEY: Model.__name__,
    'x': 'x!'
  }
}

desc_one = {
  'x': 'x',
  mc.RE_DEFS_SPEC_KEY: {
    'x': 'x!'
  }
}


desc_two = {
  'x': 'x',
  mc.CACHE_PREEMPT_ENABLED_FLAG: {
    'x': 'x!!',
  },
  mc.RE_DEFS_SPEC_KEY: {
    'x': 'x!'
  }
}


desc_three = {
  'x': 'x',
  mc.CACHE_PREEMPT_ENABLED_FLAG: {
    'x': 'x!!',
  },
  mc.RE_DEFS_SPEC_KEY: {
    'x': 'x!'
  }
}


redef_conf = {
  'x': 'x',
  mc.RE_DEFS_SPEC_KEY: {
    'x': 'x!'
  }
}


desc_five = {
  'x': 'x',
  mc.CACHE_PREEMPT_ENABLED_FLAG: {
    'x': 'x!!',
    'y': 'y!!'
  }
}


class VirtualAttrsModel(Model):
  @model_attr(key='x', cached=True)
  def x(self):
    return 'x!'

  @model_attr(key='y', cached=False)
  def y(self):
    return 'y!'

class ChildClass(Model):
  pass
