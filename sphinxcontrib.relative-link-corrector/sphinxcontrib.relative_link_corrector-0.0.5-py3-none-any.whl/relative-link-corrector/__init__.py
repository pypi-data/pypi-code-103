"""
    sphinxcontrib.relative-link-corrector
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    A Sphinx extension to correct relative links when using .md as an input.

    :copyright: Copyright 2020 Nokia
    :license: Apache License 2.0, see LICENSE for details.
"""
import os as _os
from . import implementation as _impl

if False:
    # For type annotations
    from typing import Any, Dict  # noqa
    from sphinx.application import Sphinx  # noqa

def setup(app):
    app.connect('build-finished', _impl.relative_link_corrector)

    return {
        'parallel_read_safe': True,
        'parallel_write_safe': True,
    }
