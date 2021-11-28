"""
Sphindexer
~~~~~~~~~~
A Sphinx Indexer.

:copyright: Copyright 2021 by @koKekkoh.
:license: BSD, see LICENSE for details.
"""

from typing import Any, Dict, List, Tuple

from . import rack, patch as pch, glossary as gl

__copyright__ = 'Copyright (C) 2021 @koKekkoh'
__license__   = 'BSD 2-Clause License'
__author__    = '@koKekkoh'
__version__   = '0.10.2.1'  # 2021-11-28
__url__       = 'https://github.com/KaKkouo/sphindexer'

# ------------------------------------------------------------


class Subterm(rack.Subterm): pass
class IndexUnit(rack.IndexUnit): pass
class IndexEntry(rack.IndexEntry): pass
class IndexRack(rack.IndexRack): pass


# ------------------------------------------------------------


class Glossary(gl.BaseGlossary): pass


class XRefIndex(pch.XRefIndex): pass


class HTMLBuilder(pch.BaseHTMLBuilder):

    name = 'idxr'

    def index_adapter(self) -> None:
        return IndexRack(self).create_index()


# ------------------------------------------------------------


def setup(app) -> Dict[str, Any]:

    app.add_builder(HTMLBuilder)
    app.add_directive('glossary', Glossary, True)

    return {'version': __version__,
            'parallel_read_safe': True,
            'parallel_write_safe': True,
            }


# ------------------------------------------------------------
