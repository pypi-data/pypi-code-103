from kama_sdk.model.humanizer.quantity_humanizer import QuantityHumanizer
from kama_sdk.model.supplier.base import supplier
from kama_sdk.model.supplier.base.supplier import Supplier


class QuantityHumanizationSupplier(Supplier):

  def load_backend(self) -> QuantityHumanizer:
    return self.inflate_child(
      QuantityHumanizer,
      attr=BACKEND_KEY
    )

  def get_output_spec(self):
    return self.get_attr(
      supplier.OUTPUT_FMT_KEY,
      backup=QUANT_AND_UNIT_FLAG,
      lookback=False
    )

  def _compute(self) -> str:
    raw_value = self.get_attr(supplier.SRC_DATA_KEY)
    quantity = coerce_quant(raw_value)
    if backend := self.load_backend():
      return thing(self.get_output_spec(), quantity, backend)
    else:
      return str(quantity)


def coerce_quant(raw_quant) -> float:
  try:
    return float(raw_quant)
  except:
    return 0.0


def thing(flag, quantity, humanizer: QuantityHumanizer):
  if flag == QUANT_ONLY_FLAG:
    return humanizer.humanize_quantity(quantity)
  elif flag == UNIT_ONLY_FLAG:
    return humanizer.get_unit(quantity)
  elif flag == QUANT_AND_UNIT_FLAG:
    return humanizer.humanize_expr(quantity)
  else:
    print(f"danger bad humanization type {flag}")


BACKEND_KEY = 'backend'
QUANT_ONLY_FLAG = 'quantity'
UNIT_ONLY_FLAG = 'unit'
QUANT_AND_UNIT_FLAG = 'quantity-and-unit'
