# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['twalk']

package_data = \
{'': ['*']}

entry_points = \
{'console_scripts': ['twalk = twalk:main']}

setup_kwargs = {
    'name': 'twalk',
    'version': '1.0.13',
    'description': 'Condense a directory tree into a single txt file or extract it from one',
    'long_description': "# Features\ntwalk packs an entire directory tree (including files) into a single .txt file, which it then can use to regenerate that directory tree.\n\n\n# Installation\n`pip install twalk`\n\n# Usage\n```\nusage: twalk [-h] [-i] [-v] [-V | -s] {pack,unpack} path\n\nCondense a directory tree into a single txt file or extract it from one\n\npositional arguments:\n  {pack,unpack}        What to do with the specified path\n  path                 path to directory you wish to (un)pack\n\noptional arguments:\n  -h, --help           show this help message and exit\n  -i, --ignore_binary  Instead of raising an exception when encountering\n                       binary files during packing, skip them altogether\n  -v, --version        show program's version number and exit\n  -V, --verbose\n  -s, --silent\n```\n",
    'author': 'Ovsyanka',
    'author_email': 'szmiev2000@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/Ovsyanka83/twalk',
    'packages': packages,
    'package_data': package_data,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
