
from .public import PARSERS as public_parsers
try:
    from .internal import PARSERS as internal_parsers
except ImportError:
    internal_parsers = {}

PARSERS = {**public_parsers, **internal_parsers}
