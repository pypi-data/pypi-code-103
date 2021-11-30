from typing import List, TypeVar, Dict

from kama_sdk.core.core.consts import DEFAULT_TARGET

from kama_sdk.core.core import consts
from kama_sdk.model.base.mc import INFLATE_SAFELY_KW, ATTR_KW, TITLE_KEY, INFO_KEY
from kama_sdk.model.predicate.predicate import Predicate
from kama_sdk.model.base.model import Model
from kama_sdk.model.base.model_decorators import model_attr
from kama_sdk.model.variable import generic_variable
from kama_sdk.model.variable.generic_variable import GenericVariable
from kama_sdk.model.variable.manifest_variable import ManifestVariable

T = TypeVar('T', bound='Field')

class Field(Model):

  def get_id(self) -> str:
    if explicit := super(Field, self).get_id():
      return explicit
    elif variable := self.get_variable():
      if isinstance(variable, ManifestVariable):
        return variable.get_flat_key()
    else:
      return ""

  @model_attr(cached=True)
  def get_variable(self) -> GenericVariable:
    """
    Inflate child variable using 'variable' KoD. If not present,
    construct synthetic GenericVariable using own config.
    @return: GenericVariable instance
    """
    return self.inflate_child(
      GenericVariable,
      attr=VARIABLE_KEY,
      safely=True
    ) or self.inflate_child(
      GenericVariable,
      kod=self.variable_bound_config_subset()
    )

  def get_title(self) -> str:
    if value := self.get_attr(TITLE_KEY, lookback=False):
      return value
    else:
      return self.get_variable().get_title()

  def get_info(self) -> str:
    if value := self.get_attr(INFO_KEY, lookback=False):
      return value
    else:
      return self.get_variable().get_info()

  @model_attr()
  def get_bucket_type(self):
    return self.get_attr(TARGET_KEY, backup=DEFAULT_TARGET)

  def variable_bound_config_subset(self):
    relevant = generic_variable.COPYABLE_KEYS
    config = {k: self._config.get(k) for k in relevant}
    return config

  def get_visibility_predicate(self) -> Predicate:
    kwargs = {ATTR_KW: VISIBLE_KEY, INFLATE_SAFELY_KW: True}
    return self.inflate_child(Predicate, **kwargs)

  def compute_visibility(self) -> bool:
    if predicate := self.get_visibility_predicate():
      return predicate.resolve()
    return True

  def serialize_options(self) -> List[Dict]:
    return self.get_variable().get_input_model.serialize_options()

  def is_manifest_bound(self) -> bool:
    return self.is_chart_var() or self.is_inline_chart_var()

  def is_inline_chart_var(self) -> bool:
    return self.get_bucket_type() == consts.TARGET_INLINE

  def is_chart_var(self) -> bool:
    return self.get_bucket_type() == consts.TARGET_STANDARD

  def is_state_var(self) -> bool:
    return self.get_bucket_type() == consts.TARGET_STATE


TARGET_KEY = 'target'
VARIABLE_KEY = 'variable'
VISIBLE_KEY = 'visible'
