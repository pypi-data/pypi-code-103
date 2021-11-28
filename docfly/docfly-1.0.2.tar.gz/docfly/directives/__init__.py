# -*- coding: utf-8 -*-

from .autotoctree import AutoTocTree


def setup(app):
    app.add_directive("autotoctree", AutoTocTree)
