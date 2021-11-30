# Configuration file for the Sphinx documentation builder.
#
# Full list of options can be found in the Sphinx documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import os
import sys

# add the demo python code to the path, so that it can be used to demonstrate
# source links
sys.path.append(os.path.abspath("./kitchen-sink/demo_py"))

#
# -- Project information -----------------------------------------------------
#

project = "neocrym_sphinx_theme 111"
copyright = "2021, Neocrym Records Inc."
author = "Neocrym Records Inc."

#
# -- General configuration ---------------------------------------------------
#

extensions = [
    # Sphinx's own extensions
    "sphinx.ext.autodoc",
    "sphinx.ext.extlinks",
    "sphinx.ext.intersphinx",
    "sphinx.ext.mathjax",
    "sphinx.ext.todo",
    "sphinx.ext.viewcode",
    # Our custom extension, only meant for Furo's own documentation.
    "neocrym_sphinx_theme.sphinxext",
    # External stuff
    "myst_parser",
    "sphinx_copybutton",
    "sphinx_design",
    "sphinx_inline_tabs",
]
templates_path = ["_templates"]

#
# -- Options for extlinks ----------------------------------------------------
#
extlinks = {
    "pypi": ("https://pypi.org/project/%s/", ""),
}

#
# -- Options for intersphinx -------------------------------------------------
#
intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "sphinx": ("https://www.sphinx-doc.org/en/master", None),
}

#
# -- Options for TODOs -------------------------------------------------------
#
todo_include_todos = True

#
# -- Options for Markdown files ----------------------------------------------
#
myst_enable_extensions = [
    "colon_fence",
    "deflist",
]
myst_heading_anchors = 3

#
# -- Options for HTML output -------------------------------------------------
#

html_theme = "neocrym-sphinx-theme"
html_title = "neocrym_sphinx_theme"
language = "en"
html_static_path = ["_static"]
html_css_files = ["pied-piper-admonition.css"]
html_theme_options = dict(
    announcement=(
        "If you like this theme, you can "
        '<a href="https://shoutouts.dev/projects/pradyunsg/furo">'
        "express your gratitude"
        "</a>!"
    ),
    light_logo="https://static.neocrym.com/images/neocrym/v2/SVG/neocrym-rectangle-wordmark-horizontal-black-on-transparent.svg",
    dark_logo="https://static.neocrym.com/images/neocrym/v2/SVG/neocrym-rectangle-wordmark-horizontal-white-on-transparent.svg",
    sidebar_hide_name=True,
)
pygments_style = "colorful"
pygments_dark_style = "fruity"
