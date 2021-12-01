from typing import Optional

from kama_sdk.core.core import updates_man
from kama_sdk.core.core.types import InjectionsDesc
from kama_sdk.model.supplier.base.supplier import Supplier


class LatestVendorInjectionSupplier(Supplier):
  def _compute(self) -> Optional[InjectionsDesc]:
    return updates_man.latest_injection_bundle()
