from typing import List

from kama_sdk.model.base.model_decorators import model_attr
from kama_sdk.model.input.generic_input import GenericInput, OPTIONS_KEY


class ViewSpecSelectInput(GenericInput):
  @model_attr()
  def get_options(self) -> List:
    return self.get_attr(OPTIONS_KEY, backup=[], depth=100)
