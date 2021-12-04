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
# import os
# import sys
# sys.path.insert(0, os.path.abspath('.'))


# -- Project information -----------------------------------------------------

project = 'hbspark'
copyright = '2021, Kris Zhao'
author = 'Kris Zhao'

# The full version, including alpha/beta/rc tags
release = '0.0.1'


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    'sphinx.ext.intersphinx'
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = [
    
]

# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = 'sphinx_rtd_theme'

html_theme_options = {
    'collapse_navigation': False
}

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']

# -- Options for intersphinx  -------------------------------------------------

intersphinx_mapping = {
    # 'hbspark': (f'https://hbspark.readthedocs.io{pydoctor_url_path}', None)
}

extensions.append("pydoctor.sphinx_ext.build_apidocs")

import pathlib
_hbspark_root = pathlib.Path(__file__).parent.parent.parent     #Set the spark root.

pydoctor_args = {
    '--html-output={outdir}/api/',
    f'--project-base-dir={_hbspark_root}',
    f'--project-name={project}',
    f'{_hbspark_root}/src/hbspark',
}

pydoctor_url_path = '/en/{rtd_version}/api'