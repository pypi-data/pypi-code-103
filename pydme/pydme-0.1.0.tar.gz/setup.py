# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pydme']

package_data = \
{'': ['*']}

install_requires = \
['dolphin-memory-engine>=1.1.0,<2.0.0']

setup_kwargs = {
    'name': 'pydme',
    'version': '0.1.0',
    'description': 'Hook into the Dolphin emulator and manipulate the memory',
    'long_description': '# PyDME\n\n## Warning\n\n**Do not use** before at least version 1.0.0. There will probably be a lot of incompatible changes in the beginning.\n\n## Purpose\n\nIt currently only has [`dolphin-memory-engine`](https://pypi.org/project/dolphin-memory-engine/) as a dependency, but the point is to put together one big package that merges the functionality of *that* and the JIT Cache refreshing its author has implemented in a different project.',
    'author': 'Maximillian Strand',
    'author_email': 'maximillian.strand@protonmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://gitlab.com/thedisruptproject/pydme',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
