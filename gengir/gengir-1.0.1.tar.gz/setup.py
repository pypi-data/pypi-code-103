# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['gengir']

package_data = \
{'': ['*']}

install_requires = \
['astor>=0.8.1,<0.9.0', 'lxml>=4.6.4,<5.0.0', 'typer>=0.4.0,<0.5.0']

entry_points = \
{'console_scripts': ['gengir = gengir.cli:run_cli']}

setup_kwargs = {
    'name': 'gengir',
    'version': '1.0.1',
    'description': 'Generate PEP 561 stubs for the GObject introspection library. Forked from fakegir',
    'long_description': "# GenGIR: Genuine* autocompletion for your PyGObject code!\n\n\n[fakegir](https://github.com/strycore/fakegir) is a tool to build a fake python package of PyGObject modules.\n\nGenGIR is a fork of fakegir that uses modern standards and improves on usability \n\nThe main changes are:\n\n-   Use [PEP 484](https://www.python.org/dev/peps/pep-0484/) type annotations instead of docstrings\n-   Install typings as a [PEP 561](https://www.python.org/dev/peps/pep-0561/) stub\n-   Use Sphinx markup on docstrings\n-   A cli\n\nGenGIR stores the type info inside your user or venv site-packages as a package named `gi-stubs`.  \nOnce it's installed, it should be recognized by your IDE and it should provide autocompletion and typing errors.\n\n\n## Building\n\nThis project uses [poetry](https://python-poetry.org/), so make sure to have that installed\n\nThen run `poetry install` and `poetry build`. A wheel file should be created in the dist directory that can be installed using `pip install ./dist/gengir*.whl`\n\n\n## Usage\n\nThe `*.gir` with the type info files should be included with each GNOME library development package in `/usr/share/gir-1.0/`.\n\n```\ngengir [OPTIONS] [TYPES]...\n\n  Generate PEP 561 stubs for the GObject introspection library.\n\nArguments:\n  [TYPES]...  Files to use as input for the generator. If not provided it uses\n              all files in /usr/share/gir-1.0/\n\nOptions:\n  -o, --outdir PATH               Directory to store the package typings.\n                                  $site-packages/gi-stubs by default\n  --docs / --no-docs              Include docstrings in the typings  [default:\n                                  docs]\n  --gtk INTEGER                   GTK version to generate typings for\n                                  [default: 3]\n```\n\n## Editor support\n\n-   VSCode has support for stub packages out of the box.\n-   [Jedi](https://github.com/davidhalter/jedi) supports it too, so any editor using it should work.\n",
    'author': 'Santiago Cézar',
    'author_email': 'santiagocezar2013@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/santiagocezar/gengir',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
