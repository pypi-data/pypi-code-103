# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['click_extra', 'click_extra.tests']

package_data = \
{'': ['*']}

install_requires = \
['boltons>=21.0.0,<22.0.0',
 'cli-helpers>=2.2.0,<3.0.0',
 'click-log>=0.3.2,<0.4.0',
 'click>=8.0.2,<9.0.0',
 'cloup>=0.12.1,<0.13.0',
 'pyyaml>=6.0.0,<7.0.0',
 'tabulate[widechars]>=0.8.9,<0.9.0',
 'tomli>=1.2.2,<2.0.0']

setup_kwargs = {
    'name': 'click-extra',
    'version': '1.3.0',
    'description': '🌈 Extra colorization and configuration file for Click.',
    'long_description': '# Click Extra\n\n[![Last release](https://img.shields.io/pypi/v/click-extra.svg)](https://pypi.python.org/pypi/click-extra)\n[![Python versions](https://img.shields.io/pypi/pyversions/click-extra.svg)](https://pypi.python.org/pypi/click-extra)\n[![Unittests status](https://github.com/kdeldycke/click-extra/actions/workflows/tests.yaml/badge.svg?branch=main)](https://github.com/kdeldycke/click-extra/actions/workflows/tests.yaml?query=branch%3Amain)\n[![Coverage status](https://codecov.io/gh/kdeldycke/click-extra/branch/main/graph/badge.svg)](https://codecov.io/gh/kdeldycke/click-extra/branch/main)\n\n**What is Click Extra?**\n\n`click-extra` is a collection of helpers and utilities for\n[Click](https://click.palletsprojects.com), the Python CLI framework.\n\nIt provides boilerplate code and good defaults, as weel as some workarounds\nand patches that have not reached upstream yet (or are unlikely to).\n\n## Used in\n\n- [Mail Deduplicate](https://github.com/kdeldycke/mail-deduplicate#readme) - A CLI to deduplicate similar emails.\n- [Meta Package Manager](https://github.com/kdeldycke/meta-package-manager#readme) - A unifying CLI for multiple package managers.\n\n## Installation\n\nInstall `click-extra` with `pip`:\n\n```shell-session\n$ pip install click-extra\n```\n\n## Features\n\n- TOML and YAML configuration file loader\n- Colorization of help screens\n- ``--color/--no-color`` option flag\n- Colored ``--version`` option\n- Colored ``--verbosity`` option and logs\n- ``--time/--no-time`` flag to measure duration of command execution\n- Platform recognition utilities (macOS, Linux and Windows)\n- New conditional markers for `pytest`:\n    - `@skip_linux`, `@skip_macos` and `@skip_windows`\n    - `@unless_linux`, `@unless_macos` and `@unless_windows`\n    - `@destructive` and `@non_destructive`\n\n### Issues addressed by `click-extra`\n\nKeep track of things to undo if they reach upstream.\n\n[`click`](https://github.com/pallets/click):\n  - [`testing.CliRunner.invoke` cannot pass color for `Context` instantiation (#2110)](https://github.com/pallets/click/issues/2110)\n\n[`click-log`](https://github.com/click-contrib/click-log):\n  - [Add a `no-color` option, method or parameter to disable colouring globally (#30)](https://github.com/click-contrib/click-log/issues/30)\n  - [Log level is leaking between invokations: hack to force-reset it (#29)](https://github.com/click-contrib/click-log/issues/29)\n  - [Add missing string interpolation in error message (#24)](https://github.com/click-contrib/click-log/pull/24)\n  - [Add trailing dot to help text (#18)](https://github.com/click-contrib/click-log/pull/18)\n\n[`click-help-color`](https://github.com/click-contrib/click-help-colors):\n  - [Highlighting of options, choices and metavars (#17)](https://github.com/click-contrib/click-help-colors/issues/17)\n\n[`cli-helper`](https://github.com/dbcli/cli_helpers):\n  - [Replace local tabulate formats with those available upstream (#79)](https://github.com/dbcli/cli_helpers/issues/79)\n\n[`cloup`](https://github.com/janluke/cloup):\n  - [Add support for option groups on `cloup.Group` (#98)](https://github.com/janluke/cloup/issues/98)\n  - [Styling metavars, default values, env var, choices (#97)](https://github.com/janluke/cloup/issues/97) & [Highlights options, choices and metavars (#95)](https://github.com/janluke/cloup/issues/95)\n  - [Add loading of options from a TOML configuration file (#96)](https://github.com/janluke/cloup/issues/96)\n\n[`python-tabulate`](https://github.com/astanin/python-tabulate):\n  - [Add new {`rounded`,`simple`,`double`}_(`grid`,`outline`} formats (#151)](https://github.com/astanin/python-tabulate/pull/151)\n\n### TOML configuration file\n\nAllows a CLI to read defaults options from a configuration file.\n\nHere is a sample:\n\n``` toml\n# My default configuration file.\n\n[my_cli]\nverbosity = "DEBUG"\nmanager = ["brew", "cask"]\n\n[my_cli.search]\nexact = true\n```\n\n### Colorization of help screen\n\nExtend [Cloup\'s own help formatter and theme](https://cloup.readthedocs.io/en/stable/pages/formatting.html#help-formatting-and-themes) to add colorization of:\n- Options\n- Choices\n- Metavars\n\n## Dependencies\n\nHere is a graph of Python package dependencies:\n\n![click-extra dependency graph](https://github.com/kdeldycke/click-extra/raw/main/dependencies.png)\n\n## Development\n\n[Development guidelines](https://kdeldycke.github.io/meta-package-manager/development.html)\nare the same as\n[parent project `mpm`](https://github.com/kdeldycke/meta-package-manager), from\nwhich `click-extra` originated.\n',
    'author': 'Kevin Deldycke',
    'author_email': 'kevin@deldycke.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/kdeldycke/click-extra',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
