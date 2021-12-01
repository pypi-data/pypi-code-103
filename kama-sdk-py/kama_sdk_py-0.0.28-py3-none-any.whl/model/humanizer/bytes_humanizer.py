from k8kat.utils.main import units

from kama_sdk.model.humanizer.quantity_humanizer import QuantityHumanizer


class BytesHumanizer(QuantityHumanizer):

  @staticmethod
  def _humanize_quantity(value: float) -> float:
    bytes_in_unit, _ = units.mem_quant_mult(value or 0)
    return bytes_in_unit

  def _humanize_expr(self, raw_value: float) -> str:
    value_str = self.humanize_quantity(raw_value)
    return f"{value_str}{self.get_unit(raw_value)}b"

  def get_unit(self, raw_value):
    _, unit = units.mem_quant_mult(raw_value or 0)
    return unit
