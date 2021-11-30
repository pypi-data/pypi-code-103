from __future__ import annotations

from typing import Optional, List

from kama_sdk.core.core import config_man as cman_module
from kama_sdk.core.core import config_man as config_man_mod
from kama_sdk.core.core.config_man import config_man, SPACE_KW
from kama_sdk.model.base.mc import INFO_KEY, TITLE_KEY, SPACE_KEY, ID_KEY
from kama_sdk.model.base.model_decorators import model_attr
from kama_sdk.model.predicate.predicate import Predicate
from kama_sdk.model.variable.generic_variable import GenericVariable
from kama_sdk.model.variable.variable_category import VariableCategory
from kama_sdk.utils import utils


class ManifestVariable(GenericVariable):

  def get_level(self) -> str:
    return self.get_attr(OWNER_KEY, backup=config_man_mod.USER_VARS_LVL)

  @model_attr()
  def get_flat_key(self) -> str:
    if explicit := self.get_local_attr(VARIABLE_KEY_KEY):
      return explicit
    else:
      return self.get_id()

  @model_attr(key="default_value")
  def get_default_value(self) -> str:
    return config_man.read_var(self.get_flat_key(), **{
      cman_module.SPACE_KW: self.get_config_space()
    })

  @model_attr()
  def get_category(self) -> VariableCategory:
    return self.inflate_child(
      VariableCategory,
      attr=CATEGORY_KEY,
      safely=True
    )

  def get_health_predicates(self) -> List[Predicate]:
    return self.inflate_children(
      Predicate,
      attr=CORRECTNESS_PREDICATES_KEY,
      patch={'value': self.get_current_value()}
    )

  def is_user_writable(self) -> bool:
    return self.get_level() == config_man_mod.USER_VARS_LVL

  def is_safe_to_set(self) -> bool:
    return self.is_user_writable()

  def effects_felt(self) -> List[str]:
    from kama_sdk.model.variable.manifest_variable_dependency \
      import ManifestVariableDependency
    in_deps = ManifestVariableDependency.list_for_variable(self, 'in')
    return ManifestVariableDependency.effects(in_deps, [True])

  def is_read_blocked(self) -> bool:
    effects = self.effects_felt()
    from kama_sdk.model.variable.manifest_variable_dependency_instance import EFFECT_PREVENTS_READ
    return EFFECT_PREVENTS_READ in effects

  def get_problems(self) -> List[Predicate]:
    failed_predicates = []
    for predicate in self.get_health_predicates():
      if not predicate.resolve():
        failed_predicates.append(predicate)
    return failed_predicates

  def has_problems(self) -> bool:
    return len(self.get_problems()) > 0

  def is_correct(self) -> bool:
    return not self.has_problems()

  @model_attr(key="value")
  def get_current_value(self, **kwargs) -> Optional[str]:
    down_kwargs = {**kwargs, SPACE_KW: self.get_config_space()}
    return config_man.read_var(self.get_flat_key(), **down_kwargs)

  def current_or_default_value(self):
    return self.get_current_value() or self.get_default_value()

  def is_currently_valid(self) -> bool:
    variables = config_man.get_merged_vars(**{
      cman_module.SPACE_KW: self.get_config_space()
    })
    is_defined = self.get_flat_key() in utils.deep2flat(variables).keys()
    crt_val = utils.deep_get(variables, self.get_flat_key())
    return self.validate(crt_val)['met'] if is_defined else True

  # noinspection PyBroadException
  @classmethod
  def find_or_synthesize(cls, id_or_key: str, space_id: str) -> ManifestVariable:
    pool = cls.inflate_all(selector=dict(space=space_id))
    finder = lambda m: m.get_id() == id_or_key
    if inst := next(filter(finder, pool), None):
      return inst
    else:
      return cls.synthesize_var_model(id_or_key, space_id)

  @staticmethod
  def synthesize_var_model(key: str, space_id: str):
    return ManifestVariable.inflate({
      ID_KEY: key,
      OWNER_KEY: config_man_mod.USER_VARS_LVL,
      SPACE_KEY: space_id,
      TITLE_KEY: '',
      INFO_KEY: ''
    })


OWNER_KEY = 'owner'
VARIABLE_KEY_KEY = 'flat_key'
CATEGORY_KEY = 'category'
CORRECTNESS_PREDICATES_KEY = 'health_predicates'
