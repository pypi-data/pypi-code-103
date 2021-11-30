from typing import Optional

from kama_sdk.model.base.model_decorators import model_attr
from kama_sdk.model.supplier.base.supplier import Supplier
from kama_sdk.utils.logging import lerr


class PercentageSupplier(Supplier):
  """
  Given either a `fraction` (e.g 1.3) or `numerator`/`denominator`
  (e.g 1 and 3.0), supply the corresponding percentage.

  Accepts an optional `rounding` If 0 or `None`, an integer with no
  decimal parts is returned, otherwise, the number of digits after
  period will be equal to `rounding`.
  """

  @model_attr()
  def get_numerator(self) -> Optional[float]:
    return float(self.get_attr(NUMERATOR_KEY))

  @model_attr()
  def get_denominator(self) -> Optional[float]:
    return float(self.get_attr(DENOMINATOR_KEY))

  @model_attr()
  def get_rounding(self) -> int:
    return int(self.get_attr(ROUNDING_KEY, backup=0))

  @model_attr()
  def get_fraction(self) -> float:
    if (explicit := self.get_attr(FRACTION_KEY)) is not None:
      return float(explicit)
    else:
      numerator = self.get_numerator()
      denominator = self.get_denominator()
      return numerator / denominator

  def _compute(self) -> float:
    try:
      fraction = self.get_fraction()
      rounding = self.get_rounding()
      percentage = fraction * 100.0
      if not rounding or rounding == 0:
        return int(percentage)
      else:
        return round(percentage, rounding + 1)
    except:
      lerr(f"failed to make pct", sig=self.sig())
      return 0


NUMERATOR_KEY = 'numerator'
DENOMINATOR_KEY = 'denominator'
FRACTION_KEY = 'fraction'
ROUNDING_KEY = 'rounding'
