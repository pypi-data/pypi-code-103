# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'mcp23s17'}

modules = \
['MCP23017', 'MCP23S17']
setup_kwargs = {
    'name': 'hw101',
    'version': '0.1.1',
    'description': '',
    'long_description': None,
    'author': 'Marco Bakera',
    'author_email': 'bakera@tbs1.de',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://hw101.tbs1.de',
    'package_dir': package_dir,
    'py_modules': modules,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
