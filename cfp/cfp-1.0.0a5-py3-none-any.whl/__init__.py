import importlib.resources as pkg_resources

from cfp.sources import FromParameterStore
from cfp.stack_parameters import StackParameters
from cfp.types import ApiParameter

with pkg_resources.open_text(__package__, "VERSION") as t:
    __version__ = t.readline().strip()

__all__ = [
    "ApiParameter",
    "FromParameterStore",
    "StackParameters",
]
