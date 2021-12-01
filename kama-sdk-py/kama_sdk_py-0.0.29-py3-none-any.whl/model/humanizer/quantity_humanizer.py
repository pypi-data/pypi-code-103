from abc import ABC

from kama_sdk.model.base.model_decorators import model_attr
from kama_sdk.utils.logging import lwar
from kama_sdk.model.base.model import Model


class QuantityHumanizer(Model, ABC):

  @model_attr()
  def get_rounding(self):
    return self.get_attr(ROUNDING_KEY, backup=0)

  @model_attr()
  def get_prefix(self):
    return self.get_attr(PREFIX_KEY, backup=0)

  @model_attr()
  def get_suffix(self):
    return self.get_attr(SUFFIX_KEY, backup=0)

  def get_unit(self, raw_value):
    pass

  def humanize_quantity(self, raw_quantity: float) -> float:
    try:
      better_quantity = self._humanize_quantity(raw_quantity)
      if self.get_rounding() > 0:
        return round(better_quantity, self.get_rounding())
      else:
        return int(better_quantity)
    except:
      lwar(f"humanize_quantity {raw_quantity}")
      return raw_quantity

  def humanize_expr(self, raw_value: float) -> str:
    better_expr = self._humanize_expr(raw_value)
    return f"{self.get_prefix()}{better_expr}{self.get_suffix()}"

  def _humanize_expr(self, raw_value: float) -> str:
    return str(self.humanize_quantity(raw_value))

  @staticmethod
  def _humanize_quantity(value: float) -> float:
    return value


ROUNDING_KEY = 'rounding'
PREFIX_KEY = 'prefix'
SUFFIX_KEY = 'suffix'
