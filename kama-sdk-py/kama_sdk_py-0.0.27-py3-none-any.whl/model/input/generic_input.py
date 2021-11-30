from typing import Dict, List, Any, Optional

from kama_sdk.core.core.types import InputOption
from kama_sdk.model.base.model import Model
from kama_sdk.model.base.model_decorators import model_attr


class GenericInput(Model):

  @model_attr()
  def get_options(self) -> List[InputOption]:
    return self.get_attr(OPTIONS_KEY, backup=[])

  def compute_inferred_default(self) -> Optional[Any]:
    options = self.get_options()
    if len(options) > 0:
      return options[0].get('id')
    return None

  def serialize_options(self) -> List[InputOption]:
    return self.get_options()

  def get_extras(self) -> Dict[str, any]:
    return {}

  @staticmethod
  def sanitize_for_validation(value: Any) -> Any:
    return value


OPTIONS_KEY = 'options'
