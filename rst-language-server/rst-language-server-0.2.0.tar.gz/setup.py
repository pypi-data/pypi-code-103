# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['rst_language_server']

package_data = \
{'': ['*']}

install_requires = \
['click>=8.0.3,<9.0.0', 'docutils>=0.18,<0.19', 'pygls>=0.11.3,<0.12.0']

entry_points = \
{'console_scripts': ['rst-ls = rst_language_server.cli:main']}

setup_kwargs = {
    'name': 'rst-language-server',
    'version': '0.2.0',
    'description': 'Server implementation of the Language Server Protocol for reStructuredText',
    'long_description': '===================\nRST Language Server\n===================\n|license| |version| |supported-versions|\n\nRST Language Server implements the server side of the `Language Server Protocol`_ (LSP) for the `reStructuredText`_ markup language.\n\nRST Language Server is intended to be used by text editors implementing the client side of the protocol. See `langserver.org <https://langserver.org/#implementations-client>`_ for a list of implementing clients.\n\n.. _reStructuredText: https://docutils.sourceforge.io/rst.html\n.. _Language Server Protocol: https://microsoft.github.io/language-server-protocol/\n\nFeatures\n========\nAutocompletion of title adornments\n\n.. image:: https://raw.githubusercontent.com/digitalernachschub/rst-language-server/a4c81b4805d8ea913042c82e73eb8bae56e88c58/assets/autocomplete_title_adornments.webp\n\nInstallation\n============\nRST Language Server is available as a package on PyPI and can be installed via `pip`:\n\n.. code:: sh\n\n    $ pip install --user rst-language-server\n\nUsage with Kate\n===============\n\nUsing RST Language Server with `Kate`_ requires the `LSP Client Plugin`_. Once the plugin is activated in the settings a new settings symbol named *LSP-Client* appears. Click on the section, select the *User Server Settings* tab and paste the following server configuration.\n\n.. code:: json\n\n    {\n        "servers": {\n            "rst": {\n                "command": ["rst-ls", "--client-insert-text-interpretation=false"],\n                "highlightingModeRegex": "^reStructuredText$"\n            }\n        }\n    }\n\nThis will start RST Language Server when opening any file that is configured to use the reStructuredText syntax highlighting.\n\n.. _Kate: https://apps.kde.org/kate/\n.. _LSP Client Plugin: https://docs.kde.org/stable5/en/kate/kate/kate-application-plugin-lspclient.html\n\nUsage with Neovim\n=================\nThere are numerous ways to use Language Servers in with Neovim. This setup configuration assumes that you use `nvim-lspconfig`_.\n\nTo registers RST Language Server with nvim-lspconfig, add the following lua code before requiring `lspconfig` and calling the corresponding `setup` function of the language server:\n\n.. code::\n\n  -- Register rst-ls with lspconfig\n  local configs = require "lspconfig/configs"\n  local util = require "lspconfig/util"\n\n  configs.rst_language_server = {\n    default_config = {\n      cmd = { "rst-ls" },\n      filetypes = { "rst" },\n      root_dir = util.path.dirname,\n    },\n    docs = {\n      description = [[\n  https://github.com/digitalernachschub/rst-language-server\n  Server implementation of the Language Server Protocol for reStructuredText.\n  ]],\n      default_config = {\n        root_dir = [[root_pattern(".git")]],\n      },\n    },\n  }\n\nNote that this setup currently `requires Neovim Nightly (0.6). <https://neovim.discourse.group/t/how-to-add-custom-lang-server-without-fork-and-send-a-pr-to-nvim-lspconfig-repo-resolved/1170/1>`_\n\n.. _nvim-lspconfig: https://github.com/neovim/nvim-lspconfig\n\nIs my editor supported?\n=======================\nRST Language Server can be used with any text editor that implements a Language Client. See `this list <https://langserver.org/#implementations-client>`_ of Language Client implementations.\n\nFeature Matrix\n--------------\n+------------------------------------+------+--------+\n| Feature \\\\ Editor                  | Kate | Neovim |\n+====================================+======+========+\n| Autocompletion of title adornments | ✔    | ✔      |\n+------------------------------------+------+--------+\n\n\nDevelopment configuration with Kate\n===================================\nThe RST Language Server is executed as a subprocess of the Language Client. Therefore, if we want to see log output in Kate we need to write the logs to a file using the `--log-file` command line option. We also set the log level to `debug` in order to view the JSON-RPC messages exchanged between client and server. Lastly, we configure the `root` (i.e. the working directory of the executed command) to the directory where our source code lives in and use `poetry run` to execute the code in the Git repository:\n\n.. code:: json\n\n    {\n        "servers": {\n            "rst": {\n                "command": ["poetry", "run", "rst-ls", "--log-file=/tmp/rst-ls.log", "--log-level=debug", "--client-insert-text-interpretation=false"],\n                "root": "/path/to/rst-language-server-repo",\n                "highlightingModeRegex": "^reStructuredText$"\n            }\n        }\n    }\n\n\n.. |supported-versions| image:: https://img.shields.io/pypi/pyversions/rst-language-server?style=flat-square\n.. |version| image:: https://img.shields.io/pypi/v/rst-language-server?style=flat-square\n.. |license| image:: https://img.shields.io/pypi/l/rst-language-server?style=flat-square\n',
    'author': 'Michael Seifert',
    'author_email': 'm.seifert@digitalernachschub.de',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/digitalernachschub/rst-language-server',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
