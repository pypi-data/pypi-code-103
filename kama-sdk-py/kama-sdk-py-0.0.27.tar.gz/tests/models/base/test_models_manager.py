import unittest

from kama_sdk.model.base.mc import SPACE_KEY, KIND_KEY, ID_KEY

from kama_sdk.model.base.mc import CONFIG_SPACE_KEY
from kama_sdk.model.base.model import Model
from kama_sdk.model.base.models_manager import models_manager


class TestModelsManager(unittest.TestCase):

  def setUp(self) -> None:
    models_manager.clear(restore_defaults=False)

  def test_configs_of_kind(self):
    configs = [{'kind': 'K1'}, {'kind': 'K2'}, {'kind': 'K3'}]
    classes = [K1, K3]

    actual = models_manager.configs_for_classes(configs, classes)
    self.assertEqual([{'kind': 'K1'}, {'kind': 'K3'}], actual)

  def test_find_class_by_name(self):
    models_manager.add_models([K1, K3])
    actual = models_manager.find_model_class(K1.__name__, Model)
    self.assertEqual(K1, actual)

  def test_query_descriptor_live(self):
    models_manager.add_any_descriptors([
      {KIND_KEY: Model.__name__, ID_KEY: 'one'},
      {KIND_KEY: Model.__name__, ID_KEY: 'two', SPACE_KEY: 'yy'}
    ], 'xx')
    result = Model.inflate_all(q={SPACE_KEY: 'xx'})
    self.assertEqual(1, len(result))
    self.assertEqual("one", result[0].get_id())

  def test_query_descriptor(self):
    models_manager.add_any_descriptors(hard_descriptors, 'xx')
    result = models_manager.query_descriptors({'kind': 'One'})
    self.assertEqual(1, len(result))
    self.assertEqual('One', result[0].get('kind'))

    result = models_manager.query_descriptors({'space': 'expl_space'})
    self.assertEqual(2, len(result))
    self.assertEqual('Four', result[0].get('kind'))
    self.assertEqual('Five', result[1].get('kind'))

  def test_add_descriptor_ordering(self):
    models_manager.add_any_descriptors(hard_descriptors)
    actual = [d.get(KIND_KEY) for d in models_manager.query_descriptors()]
    self.assertEqual(['One', 'Two', 'Three', 'Four', 'Five'], actual)


hard_descriptors = [
  {
    KIND_KEY: 'One'
  },
  {
    KIND_KEY: 'Two',
    SPACE_KEY: None
  },
  {
    KIND_KEY: 'Three',
    CONFIG_SPACE_KEY: 'expl_config_space'
  },
  {
    KIND_KEY: 'Four',
    SPACE_KEY: 'expl_space'
  },
  {
    KIND_KEY: 'Five',
    SPACE_KEY: 'expl_space',
    CONFIG_SPACE_KEY: 'expl_config_space'
  }
]


class K1(Model):
  pass


class K3(Model):
  pass
