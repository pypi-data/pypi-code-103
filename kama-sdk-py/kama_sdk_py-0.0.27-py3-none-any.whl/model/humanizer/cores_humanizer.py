from k8kat.utils.main import units

from kama_sdk.model.humanizer.quantity_humanizer import QuantityHumanizer


class CoresHumanizer(QuantityHumanizer):

  def _humanize_expr(self, raw_value: float) -> str:
    raw_value = 0 if raw_value is None else raw_value
    return units.humanize_cpu_quant(raw_value, with_unit=True)
