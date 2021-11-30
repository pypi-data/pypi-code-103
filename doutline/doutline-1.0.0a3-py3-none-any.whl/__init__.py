from importlib.resources import open_text

from doutline.outline import OutlineNode

with open_text(__package__, "VERSION") as t:
    __version__ = t.readline().strip()

__all__ = [
    "OutlineNode",
]
