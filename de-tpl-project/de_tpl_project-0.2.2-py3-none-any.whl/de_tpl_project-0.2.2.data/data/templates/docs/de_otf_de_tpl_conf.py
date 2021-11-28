"""
configuration file for the Sphinx documentation builder
=======================================================

this file only contains a selection of the most common options. for a full list see the documentation at
`http://www.sphinx-doc.org/en/master/config`__.

recommended section header underlines (see also `https://devguide.python.org/documenting/#sections`__ and
`https://www.sphinx-doc.org/en/master/usage/restructuredtext/basics.html#sections`__):

    # with over-line, for parts
    * with over-line, for chapters
    =, for sections
    -, for subsections
    ^, for sub-subsections
    ", for paragraphs


ReadTheDocs Server Infrastructure Configuration
===============================================

go to `https://readthedocs.org/dashboard/{package_name}/advanced`__ (Admin/Advanced Settings) to change/set
the following fields to:

    * Global settings/Default branch: **develop**
    * Default Settings/Requirements file: **requirements.txt**
    * Default Settings/Install Project: **check**ec
    * Default Settings/Use system packages: **check**

"""
import os
import sys

# -- path setup -------------------------------------------------------------------------------------------------------
#
# this file is stored in the {DOCS_FOLDER} folder directly under the project root folder. if extensions (or modules to
# document with autodoc) are in another directory, add these directories to sys.path here.
project_path = os.path.dirname(os.path.dirname(__file__))       # or: ae.base.norm_path('..')
sys.path.insert(0, project_path)                                # add root folder of this project

# found at https://github.com/readthedocs/sphinx_rtd_theme - BUT NOT NEEDED
# import sphinx_rtd_theme


# -- project information ----------------------------------------------------------------------------------------------
#
# resulting in PEP8 error E402 (with pylint use comment: # pylint: disable=E402)
# .. and because the next PyCharm inspection suppress comment did not work, now E402 gets ignored in project settings
# noinspection PyPep8
from de.setup_project import pev_str, project_env_vars


root_pev = project_env_vars(project_path=project_path)
docs_require = pev_str(root_pev, 'docs_require')
repo_root = pev_str(root_pev, 'repo_root')
project = pev_str(root_pev, 'project_desc')
author = pev_str(root_pev, 'STK_AUTHOR')
# copyright = str(datetime.datetime.now().year) + ", " + author
version = pev_str(root_pev, 'package_version')


# -- general configuration --------------------------------------------------------------------------------------------
#
# add any Sphinx extension module names here, as strings. they can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
# ---
# sphinx_rtd_theme is since Sphinx 1.4 no longer integrated (like alabaster)
# sphinx_autodoc_typehints gets automatically used by adding it to {REQ_TEST_FILE_NAME}
extensions = [
    # 'sphinx.ext.autodoc',         # automatically added by autosummary
    'sphinx.ext.autosummary',
    'sphinx.ext.viewcode',          # include package module source code
    'sphinx.ext.intersphinx',
    'sphinx.ext.graphviz',
    # 'sphinx.ext.coverage',        # not needed because all covered; test by adding to "make html" the "-b coverage"
    # .. option and then check _build/coverage/python.txt (or add it to index.rst).
    'sphinx.ext.autosectionlabel',  # create refs for all titles, subtitles
    'sphinx_rtd_theme',
]
# --- add the extensions that have to be installed via pip ---
extensions.extend(docs_require)

# -- autodoc config
# None==enabled (True failing on RTD builds - replaced with None) - see https://github.com/sphinx-doc/sphinx/issues/5459
enabled = None
autodoc_default_options = dict(
    autosummary_generate=enabled,
    members=enabled,
)
autodoc_default_options['member-order'] = 'bysource'
autodoc_default_options['private-members'] = enabled
autodoc_default_options['special-members'] = enabled,
autodoc_default_options['undoc-members'] = enabled,
autodoc_default_options['show-inheritance'] = enabled,
autodoc_default_options['exclude-members'] = ", ".join(
    ('_abc_impl', '_abc_cache', '_abc_negative_cache', '_abc_negative_cache_version', '_abc_registry',
     '__abstractmethods__', '__annotations__', '__atom_members__', '__dict__', '__module__', '__slots__', '__weakref__',
     ))

autosummary_generate = True
add_module_names = False
add_function_parentheses = True
numfig = True

# add any paths that contain templates here, relative to this directory.
# templates_path = ['_templates', '_templates/autosummary']

# list of patterns, relative to source directory, that match files and directories to ignore when looking for source
# files. this pattern also affects html_static_path and html_extra_path.
# exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']
exclude_patterns = [pev_str(root_pev, 'TPL_FILE_NAME_PREFIX') + "*"]

# example configuration for intersphinx: refer to the Python standard library
# - found at https://www.mankier.com/1/sphinx-all and https://github.com/traverseda/pycraft/blob/master/docs/conf.py.
intersphinx_mapping = dict(
    python=('https://docs.python.org/' + '.'.join(map(str, sys.version_info[0:2])), None),
    kivy=("https://kivy.org/doc/stable/", None),
)

# -- options for HTML output -------------------------------------------------

# the theme to use for HTML and HTML Help pages. see the documentation for a list of builtin themes.
html_theme = 'sphinx_rtd_theme'  # 'alabaster'

# NEXT TWO VARIABLES TAKEN FROM https://github.com/romanvm/sphinx_tutorial/blob/master/docs/conf.py
# theme options are theme-specific and customize the look and feel of a theme further. for a list of options available
# for each theme, see the documentation.
# alabaster theme options - DON'T WORK WITH sphinx_rtd_theme!!!
if html_theme == 'alabaster':
    html_theme_options = dict(
        gitlab_button=True,
        gitlab_type='star&v=2',  # use v2 button
        gitlab_user=pev_str(root_pev, 'repo_group'),
        gitlab_repo=pev_str(root_pev, 'package_name'),
        gitlab_banner=True,
    )

    # custom sidebar templates, maps document names to template names. sidebars configuration for alabaster theme:
    html_sidebars = dict()
    html_sidebars['**'] = [
        'about.html',
        'navigation.html',
        'searchbox.html',
    ]

elif html_theme == 'sphinx_rtd_theme':
    html_theme_path = ["_themes", ]
    # see https://sphinx-rtd-theme.readthedocs.io/en/latest/configuring.html
    html_theme_options = dict(
        display_version=True,
        # gitlab_url=f"{repo_root}/{package_name}/docs/index.rst",  # RTD theme offers instead as file-wide metadata
        navigation_depth=-1,
        prev_next_buttons_location='both',
        sticky_navigation=True,
        # removed in V 0.1.68: style_external_links=True,
    )

# prevent RTD build fail with 'contents.rst not found' error
# .. see https://github.com/readthedocs/readthedocs.org/issues/2569
master_doc = 'index'        # Sphinx default is 'index', whereas RTD default is 'contents'


# workaround Kivy bug until fixing PR #7435 get released (with Kivy 2.1.0)
os.environ['KIVY_DOC'] = '1'
os.environ['KIVY_NO_ARGS'] = '1'
