from importlib.resources import open_text

with open_text(__package__, "VERSION") as t:
    __version__ = t.readline().strip()

from asking.ask import ask, demo
from asking.loaders import (
    DictionaryLoader,
    FileLoader,
    YamlResourceLoader,
    YamlStringLoader,
)
from asking.models import Script
from asking.state import State

__all__ = [
    "ask",
    "demo",
    "DictionaryLoader",
    "FileLoader",
    "Script",
    "State",
    "YamlResourceLoader",
    "YamlStringLoader",
]
