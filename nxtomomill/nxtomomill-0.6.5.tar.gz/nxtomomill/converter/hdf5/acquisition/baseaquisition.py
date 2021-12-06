from silx.utils.deprecation import deprecated_warning

deprecated_warning(
    type_="Module",
    name="baseaquisition",
    reason="typo in module name",
    replacement="baseacquisition",
    since_version="0.6",
)
from .baseacquisition import *
