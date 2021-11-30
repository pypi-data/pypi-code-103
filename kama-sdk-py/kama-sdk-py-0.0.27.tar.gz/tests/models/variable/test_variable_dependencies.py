from typing import List

from kama_sdk.core.core.config_man import config_man
from kama_sdk.model.base.models_manager import models_manager
from kama_sdk.model.variable.manifest_variable_dependency import ManifestVariableDependency, \
  ManifestVariableDependencyInstance
from kama_sdk.utils.unittest import var_test_helpers
from kama_sdk.utils.unittest.base_classes import ClusterTest


DepInst = ManifestVariableDependencyInstance

class TestManifestVariableDependency(ClusterTest):
  """
  Look at var_test_helpers.py for the descriptors. What `dependency-one`
  says is "one.one has a potential dependency on one.two and two.two
  that is active only for two.two". It's a nonsensical dependency IRL but
  easy to write here.
  """
  def setUp(self) -> None:
    super(TestManifestVariableDependency, self).setUp()
    models_manager.add_descriptors([
      *var_test_helpers.variable_descriptors,
      *var_test_helpers.dependency_descriptor
    ])
    config_man.patch_user_vars({'two': {'one': 'x', 'two': 'y'}})

  def test_synth_child_variable_ids(self):
    inst = ManifestVariableDependency.inflate("dependency-one")
    dep_insts = inst.generate_synthetic_child_instances()
    self.assertEqual('one.one', dep_insts[0].get_from_variable().get_id())
    self.assertEqual('two.one', dep_insts[0].get_to_variable().get_id())
    self.assertEqual('one.one', dep_insts[1].get_from_variable().get_id())
    self.assertEqual('two.two', dep_insts[1].get_to_variable().get_id())

  def test_synth_child_predicate_value_availability(self):
    inst = ManifestVariableDependency.inflate("dependency-one")
    dep_insts = inst.generate_synthetic_child_instances()
    pred_one = dep_insts[0].get_check_active_predicate()
    pred_two = dep_insts[1].get_check_active_predicate()
    self.assertEqual("x", pred_one.get_challenge())
    self.assertEqual("y", pred_two.get_challenge())

  def test_active(self):
    inst = ManifestVariableDependency.inflate("dependency-one")
    dep_insts = inst.generate_synthetic_child_instances()
    self.assertFalse(find_dep_inst('two.one', dep_insts).is_active())
    self.assertTrue(find_dep_inst('two.two', dep_insts).is_active())


def find_dep_inst(_id: str, instances: List[DepInst]) -> DepInst:
  finder = lambda inst: inst.get_to_variable().get_id() == _id
  return next(filter(finder, instances), None)
