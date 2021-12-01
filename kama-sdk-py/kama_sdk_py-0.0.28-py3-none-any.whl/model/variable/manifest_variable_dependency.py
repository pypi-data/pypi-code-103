from __future__ import annotations

from functools import lru_cache
from typing import List

from kama_sdk.model.base import mc
from kama_sdk.model.base.mc import QUERY_KW, INFO_KEY, TITLE_KEY
from kama_sdk.model.base.model import Model
from kama_sdk.model.variable.manifest_variable import ManifestVariable
from kama_sdk.model.variable.manifest_variable_dependency_instance import ManifestVariableDependencyInstance, \
  TO_SINGLE_KEY, FROM_SINGLE_KEY, ACTIVE_CHECK_PRED_KEY, EFFECT_KEY

MVar = ManifestVariable
DepInst = ManifestVariableDependencyInstance


class ManifestVariableDependency(Model):
  """
  Represents a logical dependency relationship between one set of
  manifest variables and another. Similar to a bipartite graph where
  the left side is `from: List[ManifestVariable]` and the right side is
  `to: List[ManifestVariable]`.

  Each group is designated using standard model associations. When, below,
  we refer to a "direction", `out` means from left to right e.g how
  `to` variables depend on `from` variables.

  A dependency is characterized by its state (active or not) and its effect
  (one group of variables prevents anther group from being read, one group
  compels the other to have non-null values, etc...). The former is gotten
  by evaluating the `activation_predicate: Predicate` attribute. The latter by
  reading the `effect` attribute.
  """
  @classmethod
  def list_for_variable(cls, variable: MVar, direction: str) -> List[VarDep]:
    """
    For a given manifest variable `variable: ManifestVariable`, and a
    `direction: str`
    returns the `ManifestVariableDependency`s that list `variable` on
    the `direction` side. So if the dependency are
    `dep_one = ManifestVariableDependency(from=[a], to=[b, c])` and
    `dep_two = ManifestVariableDependency(from=[a], to=[d])`, then
    `f(b, 'to')` would give `[dep_one]` because it is in `dep_one`'s `to`.
    :param direction: "in" or "out"
    :param variable:
    :return: list of inflated instances that match
    """
    down_kwargs = {QUERY_KW: {mc.SPACE_KEY: variable.get_space_id()}}
    all_dependencies = cls.inflate_all(**down_kwargs)

    variable_dependencies = []

    for dependency in all_dependencies:
      if direction == 'out':
        other_var_ids = [v.get_id() for v in dependency.from_variables()]
      else:
        other_var_ids = [v.get_id() for v in dependency.to_variables()]
      if variable.get_flat_key() in other_var_ids:
        variable_dependencies.append(dependency)

    return variable_dependencies

  @lru_cache
  def generate_synthetic_child_instances(self) -> List[DepInst]:
    """

    :return:
    """
    results = []

    simple_active_check_pred = self.get_config().get(ACTIVE_CHECK_PRED_KEY)
    simple_effect = self.get_config().get(EFFECT_KEY)

    for from_variable in self.from_variables():
      for to_variable in self.to_variables():
        dependency_instance = DepInst.inflate({
          TITLE_KEY: self.get_title(),
          INFO_KEY: self.get_info(),
          FROM_SINGLE_KEY: from_variable,
          TO_SINGLE_KEY: to_variable,
          ACTIVE_CHECK_PRED_KEY: simple_active_check_pred,
          EFFECT_KEY: simple_effect
        })
        dependency_instance.set_parent(self)
        results.append(dependency_instance)
    return results

  @lru_cache
  def from_variables(self) -> List[ManifestVariable]:
    from kama_sdk.model.variable.manifest_variable import ManifestVariable
    return self.inflate_children(ManifestVariable, attr=FROM_KEY)

  @lru_cache
  def to_variables(self) -> List[ManifestVariable]:
    from kama_sdk.model.variable.manifest_variable import ManifestVariable
    return self.inflate_children(ManifestVariable, attr=TO_KEY)

  @staticmethod
  def effects(deps: List[VarDep], active: List[bool] = None) -> List[str]:
    nested_list = []
    for dependency in deps:
      for instance in dependency.generate_synthetic_child_instances():
        if active is None or active == [True, False]:
          nested_list.append(instance.get_effect())
        elif instance.is_active() in active:
          nested_list.append(instance.get_effect())
    return list(set(nested_list))


VarDep = ManifestVariableDependency

FROM_KEY = 'from'
TO_KEY = 'to'
