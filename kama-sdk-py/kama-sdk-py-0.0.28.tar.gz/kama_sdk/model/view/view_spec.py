from typing import Dict, Optional

from kama_sdk.model.base.model import Model
from kama_sdk.utils.logging import lwar, lerr


class ViewSpec(Model):

  def compute_spec(self) -> Dict:
    try:
      return self.get_attr(SPEC_KEY, depth=100)
    except Exception as e:
      lerr(f"render error: {str(e)}", sig=self.sig(), exc=e)
      try:
        return self.get_attr(FALLBACK_SPEC_KEY, depth=100)
      except Exception as e2:
        lerr(f"fallback-render error: {str(e2)}", sig=self.sig())
        return {}

  def compute_short_circuit_spec(self) -> Optional[Dict]:
    pass


SPEC_KEY = "spec"
FALLBACK_SPEC_KEY = "fallback_spec"
SHORT_CIRCUIT_KEYS = "short_circuits"
