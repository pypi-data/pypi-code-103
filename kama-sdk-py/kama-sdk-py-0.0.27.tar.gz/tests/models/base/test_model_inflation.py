from kama_sdk.model.base import mc
from kama_sdk.model.base.model import Model
from kama_sdk.model.base.models_manager import models_manager
from kama_sdk.utils.unittest.base_classes import ClusterTest
from kama_sdk.utils.unittest import helper


class TestModelInflation(ClusterTest):
  def test_inflate_with_kind(self):
    models_manager.add_models([ChildClass])
    inflated: Model = Model.inflate_with_str(f"kind::{ChildClass.__name__}")
    self.assertIsNotNone(inflated)
    self.assertEqual(ChildClass.__name__, inflated.get_kind())

  def test_inflate_all(self):
    models_manager.clear(restore_defaults=False)
    klass = Model
    # if breaks do Model

    class L1(klass):
      pass

    class L2(L1):
      pass

    models_manager.add_any_descriptors([{
      'kind': klass.__name__,
      'id': 'lv0',
    }])

    models_manager.add_any_descriptors([{
      'kind': f"not-{klass.__name__}",
      'id': 'should-not-appear',
    }])

    models_manager.add_any_descriptors([{
      'kind': L2.__name__,
      'id': 'lv2',
    }])

    models_manager.add_models([L1, L2])

    sig = lambda inst: {'id': inst.get_id(), 'cls': inst.__class__}
    from_lv0 = list(map(sig, klass.inflate_all()))
    exp = [{'id': 'lv0', 'cls': klass}, {'id': 'lv2', 'cls': L2}]
    self.assertEqual(exp, from_lv0)

  def test_inflate_with_config_expl_cls(self):
    class SubModel(Model):
      pass

    models_manager.add_models([SubModel])
    actual = Model.inflate({'id': 'mine', 'kind': SubModel.__name__})
    self.assertEqual(SubModel, actual.__class__)

  def test_inflate_with_id(self):
    a = helper.g_conf(k='a', i=Model.__name__)
    b = helper.g_conf(k='b', i=Model.__name__)
    models_manager.add_any_descriptors([a, b])

    inflated = Model.inflate('id::a')
    self.assertEqual(type(inflated), Model)
    self.assertEqual(inflated.get_id(), 'a')
    self.assertEqual(inflated.get_title(), 'a.title')

    inflated = Model.inflate('a')
    self.assertEqual(type(inflated), Model)
    self.assertEqual(inflated.get_id(), 'a')
    self.assertEqual(inflated.get_title(), 'a.title')

  def test_inflate_with_kind_key(self):
    class Custom(Model):
      def get_info(self):
        return 'baz'

    models_manager.add_models([Custom])
    literal = f"kind::{Custom.__name__}"
    result = Model.inflate_with_str(literal)
    self.assertEqual(Custom, result.__class__)
    self.assertEqual('baz', result.get_info())

  def test_inflate_with_config_simple(self):
    inflated = Model.inflate({'title': 'foo'})
    self.assertEqual('foo', inflated.get_title())
    self.assertEqual(Model, inflated.__class__)

  def test_inflate_with_config_inherit_easy(self):
    models_manager.add_any_descriptors([{
      'kind': Model.__name__,
      'id': 'parent',
      'title': 'yours'
    }])

    actual = Model.inflate({'id': 'mine', 'inherit': 'parent'})
    self.assertEqual(Model, actual.__class__)
    self.assertEqual('mine', actual.get_id())
    self.assertEqual('yours', actual.get_title())

  def test_inflate_same_id_different_space(self):
    common = {'kind': Model.__name__, 'id': 'same'}
    models_manager.add_any_descriptors([
      {**common, mc.SPACE_KEY: 'one', 'title': 'one'},
      {**common, mc.SPACE_KEY: 'two', 'title': 'two'}
    ])

    r1 = Model.inflate("same", **{
      mc.QUERY_KW: {mc.SPACE_KEY: 'one'}
    })
    r2 = Model.inflate("same", **{
      mc.QUERY_KW: {mc.SPACE_KEY: 'two'}
    })

    self.assertEqual('one', r1.get_title())
    self.assertEqual('two', r2.get_title())

  def test_inflate_with_config_inherit_hard(self):
    models_manager.add_models([DonorModel])
    models_manager.add_any_descriptors([donor_config])

    inheritor = Model.inflate(inheritor_config)
    self.assertEqual(DonorModel, inheritor.__class__)
    self.assertEqual('inheritor-id', inheritor.get_id())
    self.assertEqual('inheritor-title', inheritor.get_title())
    self.assertEqual('donor-info', inheritor.get_info())


class ChildClass(Model):
  pass


class DonorModel(Model):
  pass


donor_config = {
  'kind': DonorModel.__name__,
  'id': 'donor-id',
  'title': 'donor-title',
  'info': 'donor-info'
}

inheritor_config = {
  'id': 'inheritor-id',
  'inherit': 'donor-id',
  'title': 'inheritor-title',
}


