from importlib.resources import open_text

with open_text(__package__, "VERSION") as t:
    __version__ = t.readline().strip()

from asking.ask import ask
from asking.models import Script
from asking.state import State
from asking.types import Responses

__all__ = [
    "ask",
    "Responses",
    "Script",
    "State",
]
