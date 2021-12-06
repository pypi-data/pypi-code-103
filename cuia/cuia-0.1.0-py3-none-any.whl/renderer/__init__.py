"""Renderer facilities."""


from .curses import CursesRenderer
from .log import LogRenderer
from .renderer import Renderer

__all__ = ["CursesRenderer", "LogRenderer", "Renderer"]


# TODO: call this module "renderers" (plural)


# TODO: make a TextRenderer
