from k8kat.utils.main import units

from kama_sdk.model.base.common import TYPE_KEY
from kama_sdk.model.supplier.base.supplier import Supplier
from kama_sdk.utils.logging import lwar


class UnitConverter(Supplier):

  def get_type(self):
    return self.get_local_attr(TYPE_KEY)

  def get_amount_in_source_unit(self) -> str:
    value = super(UnitConverter, self).get_source_data()
    if type(value) in [float, int, str]:
      return str(value)
    else:
      lwar(f"using instead of invalid {value}", sig=self.sig())
      return '0'

  def get_output_unit(self):
    return self.get_local_attr(OUTPUT_UNIT_KEY) or ''

  def _compute(self) -> float:
    amt_expression = self.get_amount_in_source_unit()
    output_unit = self.get_output_unit()
    return units.parse_quant_expr(amt_expression, output_unit)


OUTPUT_UNIT_KEY = "output_unit"
