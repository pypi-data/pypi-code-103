# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import os
import sys

sys.path.insert(0, os.path.abspath('../../..'))


# -- Project information -----------------------------------------------------

project = 'darts'
copyright = '2021, Unit8 SA'
author = 'Unit8 SA'
version = '0.14.0'


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    'sphinx.ext.autosummary',
    'sphinx.ext.autodoc',
    'sphinx.ext.viewcode',
    'sphinx.ext.todo',
    'sphinx_automodapi.automodapi',
    'sphinx.ext.graphviz',
    'sphinx.ext.napoleon',
    'sphinx.ext.githubpages',
    'nbsphinx',
    'm2r2'
]

autodoc_default_options = {
    'inherited-members': None,
    'show-inheritance': None,
    'exclude-members': 'ForecastingModel,DualCovariatesForecastingModel,TorchForecastingModel,' +
                       'PastCovariatesTorchModel,FutureCovariatesTorchModel,DualCovariatesTorchModel,' +
                       'MixedCovariatesTorchModel,SplitCovariatesTorchModel,' +
                       'TorchParametricProbabilisticForecastingModel'
}

# In order to also have the docstrings of __init__() methods included
autoclass_content = 'both'

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# The language for content autogenerated by Sphinx. Refer to documentation
# for a list of supported languages.
#
# This is also used if you do content translation via gettext catalogs.
# Usually you set "language" from the command line for these cases.
language = 'en'

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = [
    '_build', 'Thumbs.db', '.DS_Store',
    '**/modules.rst', '**/darts.tests.*',
    '**/*logging.rst'
]


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = 'pydata_sphinx_theme'
html_logo = "static/darts-logo-trim.png"

html_theme_options = {
  "github_url": "https://github.com/unit8co/darts",
  "twitter_url": "https://twitter.com/unit8co",
  "search_bar_position": "navbar",
}



# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['static']


# -- Extension configuration -------------------------------------------------

# -- Options for todo extension ----------------------------------------------

# If true, `todo` and `todoList` produce output, else they produce nothing.
todo_include_todos = False


# Ensure that otherwise excluded methods get included.
include_private_methods = ["_fill_missing_dates", "_restore_xarray_from_frequency"]
def skip(app, what, name, obj, skip, options):
    if name in include_private_methods:
        return False
    return skip

def setup(app):
    app.connect("autodoc-skip-member", skip)
