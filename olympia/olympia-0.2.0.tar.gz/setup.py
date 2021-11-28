# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['olympia']

package_data = \
{'': ['*']}

entry_points = \
{'console_scripts': ['olympia = olympia.__main__:main']}

setup_kwargs = {
    'name': 'olympia',
    'version': '0.2.0',
    'description': 'Olympia',
    'long_description': '<h1 align="center">Olympia</h1>\n<p align="center">Data structures and algorithms in Python 🐍</p>\n<p align="center">\n<a href="https://github.com/lukemiloszewski/olympia/actions/workflows/ci.yml/badge.svg" target="_blank">\n    <img src="https://github.com/lukemiloszewski/olympia/actions/workflows/ci.yml/badge.svg" alt="Continuous Integration">\n</a>\n<a href="https://codecov.io/gh/lukemiloszewski/olympia" target="_blank">\n    <img src="https://img.shields.io/codecov/c/github/lukemiloszewski/olympia?color=%2334D058" alt="Test Coverage">\n</a>\n<a href="https://pypi.org/project/olympia" target="_blank">\n    <img src="https://img.shields.io/pypi/v/olympia?color=%2334D058&label=pypi%20package" alt="Package Version">\n</a>\n<a href="https://pypi.org/project/olympia" target="_blank">\n    <img src="https://img.shields.io/pypi/pyversions/olympia.svg?color=%2334D058" alt="Supported Python Versions">\n</a>\n</p>\n\n## Installation\n\n```python\npip install olympia\n```\n\n## Usage\n\n```python\nfrom olympia import LinkedList\n\nll = LinkedList()\nll.add_last(1)\nll.add_last(2)\nll.add_last(3)\nll\n\n1 -> 2 -> 3 -> None\n```\n',
    'author': 'Luke Miloszewski',
    'author_email': 'lukemiloszewski@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/lukemiloszewski/olympia',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'entry_points': entry_points,
    'python_requires': '>=3.7.1,<4.0.0',
}


setup(**setup_kwargs)
