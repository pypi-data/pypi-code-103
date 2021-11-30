import traceback
from typing import Dict, Any

from werkzeug.utils import cached_property

from kama_sdk.model.input.generic_input import GenericInput


class SliderInput(GenericInput):
  def get_min(self) -> int:
    return self.get_attr('min', backup=0)

  def get_max(self) -> int:
    return self.get_attr('max', backup=10)

  def get_step(self) -> int:
    return self.get_attr('step', backup=1)

  def get_suffix(self):
    return self.get_attr('suffix', backup='')

  def get_extras(self) -> Dict[str, any]:
    return dict(
      min=self.get_min(),
      max=self.get_max(),
      step=self.get_step(),
      suffix=self.get_suffix()
    )

  def sanitize_for_validation(self, value: Any) -> Any:
    if value is not None and self.get_suffix():
      # noinspection PyBroadException
      try:
        return float(str(value).split(self.get_suffix())[0])
      except:
        print("[kama_sdk::slider_input] sanitize input failed:")
        print(traceback.format_exc())
        return value
    else:
      return value
