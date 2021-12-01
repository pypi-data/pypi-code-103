from __future__ import annotations

from typing import Optional

from kama_sdk.model.base.mc import INFLATE_SAFELY_KW, ATTR_KW
from kama_sdk.model.base.model import Model
from kama_sdk.model.base.model_decorators import model_attr
from kama_sdk.model.predicate.predicate import Predicate
from kama_sdk.model.variable.manifest_variable import ManifestVariable

FROM_SINGLE_KEY = 'from_variable'
TO_SINGLE_KEY = 'to_variable'


class ManifestVariableDependencyInstance(Model):
  """
  This model should only ever be inflated by its
  parent - `ManifestVariableDependency`. Users should not create
  descriptors for it or subclass it.
  """

  def get_check_active_predicate(self) -> Optional[Predicate]:
    kwarg = {INFLATE_SAFELY_KW: True, ATTR_KW: ACTIVE_CHECK_PRED_KEY}
    return self.inflate_child(Predicate, **kwarg)

  @model_attr()
  def is_active(self) -> bool:
    if predicate := self.get_check_active_predicate():
      return predicate.resolve()
    else:
      return False

  @model_attr()
  def get_effect(self) -> str:
    return self.get_config().get(EFFECT_KEY) or EFFECT_PREVENTS_READ

  @model_attr(key=FROM_SINGLE_KEY)
  def get_from_variable(self) -> ManifestVariable:
    return self.get_config().get(FROM_SINGLE_KEY)

  @model_attr(key=TO_SINGLE_KEY)
  def get_to_variable(self) -> ManifestVariable:
    return self.get_config().get(TO_SINGLE_KEY)


EFFECT_KEY = 'effect'
ACTIVE_CHECK_PRED_KEY = 'active_condition'
EFFECT_PREVENTS_READ = 'prevents_read'
