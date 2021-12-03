"""json_converter."""

from datetime import datetime
from typing import Any


def json_converter(element: Any) -> Any:
    """Converter of elements to JSONable objects."""
    if isinstance(element, datetime):
        return str(element)
    return str(element)
