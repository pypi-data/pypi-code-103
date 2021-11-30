from typing import List, TypeVar, Optional, Any

from kama_sdk.core.core.types import PredEval
from kama_sdk.model.base import mc
from kama_sdk.model.base.mc import PATCH_KEY, ATTR_KW, WEAK_PATCH_KEY
from kama_sdk.model.base.model import Model
from kama_sdk.model.base.model_decorators import model_attr
from kama_sdk.model.input.generic_input import GenericInput
from kama_sdk.model.predicate.predicate import Predicate, CHALLENGE_KEY
from kama_sdk.utils import utils
from kama_sdk.utils.logging import lerr

T = TypeVar('T', bound='GenericVariable')

class GenericVariable(Model):

  @model_attr()
  def get_default_value(self) -> Optional[Any]:
    default_value = self.get_attr(DEFAULT_VALUE_KEY)
    if default_value is None:
      if input_model := self.get_input_model():
        default_value = input_model.compute_inferred_default()
    return default_value

  @model_attr()
  def get_input_model(self) -> GenericInput:
    return self.inflate_child(
      GenericInput,
      attr=INPUT_MODEL_KEY,
      safely=True
    ) or GenericInput({})

  def get_patched_validation_predicates(self, value: Any) -> List[Predicate]:
    """
    Given a `value` to validate against, inflates validation predicates
    hot patched with 'value: value'.
    :param value:
    :return:
    """
    value = self.sanitize_for_validation(value)
    return self.inflate_children(
      Predicate,
      **{
        ATTR_KW: VALIDATION_PREDS_KEY,
        WEAK_PATCH_KEY: {CHALLENGE_KEY: value},
        PATCH_KEY: {VALUE_PATCH_KEY: value}
      }
    )

  def validate(self, value: Any) -> PredEval:
    try:
      for predicate in self.get_patched_validation_predicates(value):
        if not utils.any2bool(predicate.resolve()):
          return PredEval(
            predicate_id=predicate.get_id(),
            met=False,
            reason=predicate.get_reason(),
            tone=predicate.get_tone()
          )
    except:
      lerr(f"inflate/resolve failed for validators")
      return PredEval(
        met=False,
        tone='error',
        reason='error loading or running validator(s)'
      )
    return PredEval(
        met=True,
        tone='',
        reason=''
      )

  def current_or_default_value(self):
    return self.get_default_value()

  def sanitize_for_validation(self, value: Any) -> Any:
    if input_model := self.get_input_model():
      return input_model.sanitize_for_validation(value)
    return value


DEFAULT_VALUE_KEY = 'default'
INPUT_MODEL_KEY = 'input'
VALIDATION_PREDS_KEY = 'validators'
VALUE_PATCH_KEY = 'value'


COPYABLE_KEYS = [
  DEFAULT_VALUE_KEY,
  INPUT_MODEL_KEY,
  VALIDATION_PREDS_KEY
]
