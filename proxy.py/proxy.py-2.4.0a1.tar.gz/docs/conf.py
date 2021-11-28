# pylint: disable=invalid-name
# Requires Python 3.6+
# Ref: https://www.sphinx-doc.org/en/master/usage/configuration.html
"""Configuration for the Sphinx documentation generator."""

import sys
from functools import partial
from pathlib import Path

from setuptools_scm import get_version


# -- Path setup --------------------------------------------------------------

PROJECT_ROOT_DIR = Path(__file__).parents[1].resolve()  # pylint: disable=no-member
get_scm_version = partial(get_version, root=PROJECT_ROOT_DIR)

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.


sys.path.insert(0, str(PROJECT_ROOT_DIR))

# Make in-tree extension importable in non-tox setups/envs, like RTD.
# Refs:
# https://github.com/readthedocs/readthedocs.org/issues/6311
# https://github.com/readthedocs/readthedocs.org/issues/7182
sys.path.insert(0, str((Path(__file__).parent / '_ext').resolve()))

# -- Project information -----------------------------------------------------

github_url = 'https://github.com'
github_repo_org = 'abhinavsingh'
github_repo_name = 'proxy.py'
github_repo_slug = f'{github_repo_org}/{github_repo_name}'
github_repo_url = f'{github_url}/{github_repo_slug}'
github_sponsors_url = f'{github_url}/sponsors'

project = github_repo_name.title()
author = f'{project} project contributors'
copyright = author  # pylint: disable=redefined-builtin

# The short X.Y version
version = '.'.join(
    get_scm_version(
        local_scheme='no-local-version',
    ).split('.')[:3],
)

# The full version, including alpha/beta/rc tags
release = get_scm_version()

rst_epilog = f"""
.. |project| replace:: {project}
"""


# -- General configuration ---------------------------------------------------


# There are two options for replacing |today|: either, you set today to some
# non-false value, then it is used:
# today = ''
# Else, today_fmt is used as the format for a strftime call.
today_fmt = '%B %d, %Y'

# The reST default role (used for this markup: `text`) to use for all
# documents.
# Ref: python-attrs/attrs#571
default_role = 'any'

# If true, '()' will be appended to :func: etc. cross-reference text.
add_function_parentheses = True

# If true, the current module name will be prepended to all description
# unit titles (such as .. function::).
add_module_names = True

# If true, sectionauthor and moduleauthor directives will be shown in the
# output. They are ignored by default.
show_authors = True

# The name of the Pygments (syntax highlighting) style to use.
# pygments_style = 'sphinx'

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    # stdlib-party extensions:
    'sphinx.ext.autodoc',
    'sphinx.ext.doctest',
    'sphinx.ext.extlinks',
    'sphinx.ext.intersphinx',
    'sphinx.ext.todo',
    'sphinx.ext.coverage',
    'sphinx.ext.viewcode',

    # Third-party extensions:
    'myst_parser',  # extended markdown; https://pypi.org/project/myst-parser/
    'sphinxcontrib.apidoc',
]

# Conditional third-party extensions:
try:
    import sphinxcontrib.spelling as _sphinxcontrib_spelling
except ImportError:
    extensions.append('spelling_stub_ext')
else:
    del _sphinxcontrib_spelling
    extensions.append('sphinxcontrib.spelling')

# The language for content autogenerated by Sphinx. Refer to documentation
# for a list of supported languages.
#
# This is also used if you do content translation via gettext catalogs.
# Usually you set "language" from the command line for these cases.
language = 'en'


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
html_theme = 'furo'

html_show_sphinx = True

html_theme_options = {
}

html_context = {
}


# The name for this set of Sphinx documents.  If None, it defaults to
# "<project> v<release> documentation".
# html_title = f'{project} Documentation'

# A shorter title for the navigation bar.  Default is the same as html_title.
# html_short_title = 'Documentation'

# If not '', a 'Last updated on:' timestamp is inserted at every page bottom,
# using the given strftime format.
html_last_updated_fmt = '%b %d, %Y'

# If true, an OpenSearch description file will be output, and all pages will
# contain a <link> tag referring to it.  The value of this option must be the
# base URL from which the finished HTML is served.
# html_use_opensearch = f'https://{github_repo_name.replace(".", "")}.readthedocs.io/en/latest/'

# The master toctree document.
root_doc = master_doc = 'index'  # Sphinx 4+ / 3-  # noqa: WPS429


# -- Extension configuration -------------------------------------------------

# -- Options for intersphinx extension ---------------------------------------

intersphinx_mapping = {
    'myst': ('https://myst-parser.rtfd.io/en/latest', None),
    'python': ('https://docs.python.org/3', None),
    'python2': ('https://docs.python.org/2', None),
}

# -- Options for todo extension ----------------------------------------------

# If true, `todo` and `todoList` produce output, else they produce nothing.
todo_include_todos = True

# -- Options for sphinxcontrib.apidoc extension ------------------------------

apidoc_excluded_paths = [
    'plugin/cache/*',
    'testing/*.py',
]
apidoc_extra_args = [
    '--implicit-namespaces',
    '--private',  # include “_private” modules
]
apidoc_module_dir = str(PROJECT_ROOT_DIR / 'proxy')
apidoc_module_first = False
apidoc_output_dir = 'pkg'
apidoc_separate_modules = True
apidoc_toc_file = None

# -- Options for sphinxcontrib.spelling extension ----------------------------

spelling_ignore_acronyms = True
spelling_ignore_importable_modules = True
spelling_ignore_pypi_package_names = True
spelling_ignore_python_builtins = True
spelling_ignore_wiki_words = True
spelling_show_suggestions = True
spelling_word_list_filename = [
    'spelling_wordlist.txt',
]

# -- Options for extlinks extension ------------------------------------------

extlinks = {
    'issue': (f'{github_repo_url}/issues/%s', '#'),  # noqa: WPS323
    'pr': (f'{github_repo_url}/pull/%s', 'PR #'),  # noqa: WPS323
    'commit': (f'{github_repo_url}/commit/%s', ''),  # noqa: WPS323
    'gh': (f'{github_url}/%s', 'GitHub: '),  # noqa: WPS323
    'user': (f'{github_sponsors_url}/%s', '@'),  # noqa: WPS323
}

# -- Options for linkcheck builder -------------------------------------------

linkcheck_ignore = [
    r'http://localhost:\d+/',  # local URLs
]
linkcheck_workers = 25

# -- Options for myst_parser extension ------------------------------------------

myst_enable_extensions = [
    'colon_fence',  # allow to optionally use ::: instead of ```
    'deflist',
    'html_admonition',  # allow having HTML admonitions
    'html_image',  # allow HTML <img> in Markdown
    # FIXME: `linkify` turns "Proxy.Py` into a link so it's disabled now
    # Ref: https://github.com/executablebooks/MyST-Parser/issues/428#issuecomment-970277208
    # "linkify",  # auto-detect URLs @ plain text, needs myst-parser[linkify]
    'replacements',  # allows Jinja2-style replacements
    'smartquotes',  # use "cursive" quotes
    'substitution',  # replace common ASCII shortcuts into their symbols
]
myst_substitutions = {
  'project': project,
}

# -- Strict mode -------------------------------------------------------------

# The reST default role (used for this markup: `text`) to use for all
# documents.
# Ref: python-attrs/attrs#571
default_role = 'any'

nitpicky = True
_any_role = 'any'
_py_obj_role = 'py:obj'
_py_class_role = 'py:class'
nitpick_ignore = [
    (_any_role, '<proxy.HttpProxyBasePlugin>'),
    (_any_role, '__init__'),
    (_any_role, 'Client'),
    (_any_role, 'event_queue'),
    (_any_role, 'fd_queue'),
    (_any_role, 'flag.flags'),
    (_any_role, 'flags.work_klass'),
    (_any_role, 'flush'),
    (_any_role, 'httpx'),
    (_any_role, 'HttpParser.state'),
    (_any_role, 'HttpProtocolHandler'),
    (_any_role, 'multiprocessing.Manager'),
    (_any_role, 'proxy.core.base.tcp_upstream.TcpUpstreamConnectionHandler'),
    (_any_role, 'work_klass'),
    (_py_class_role, '_asyncio.Task'),
    (_py_class_role, 'asyncio.events.AbstractEventLoop'),
    (_py_class_role, 'CacheStore'),
    (_py_class_role, 'HttpParser'),
    (_py_class_role, 'HttpProtocolHandlerPlugin'),
    (_py_class_role, 'HttpProxyBasePlugin'),
    (_py_class_role, 'HttpWebServerBasePlugin'),
    (_py_class_role, 'multiprocessing.context.Process'),
    (_py_class_role, 'multiprocessing.synchronize.Lock'),
    (_py_class_role, 'NonBlockingQueue'),
    (_py_class_role, 'paramiko.channel.Channel'),
    (_py_class_role, 'proxy.http.parser.parser.T'),
    (_py_class_role, 'proxy.plugin.cache.store.base.CacheStore'),
    (_py_class_role, 'proxy.core.pool.AcceptorPool'),
    (_py_class_role, 'proxy.core.executors.ThreadlessPool'),
    (_py_class_role, 'proxy.core.acceptor.threadless.T'),
    (_py_class_role, 'queue.Queue[Any]'),
    (_py_class_role, 'TcpClientConnection'),
    (_py_class_role, 'TcpServerConnection'),
    (_py_class_role, 'unittest.case.TestCase'),
    (_py_class_role, 'unittest.result.TestResult'),
    (_py_class_role, 'UUID'),
    (_py_class_role, 'Url'),
    (_py_class_role, 'WebsocketFrame'),
    (_py_class_role, 'Work'),
    (_py_obj_role, 'proxy.core.acceptor.threadless.T'),
]
