# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['guacapy']

package_data = \
{'': ['*']}

install_requires = \
['requests>=2.26.0,<3.0.0', 'simplejson>=3.17.2,<4.0.0']

setup_kwargs = {
    'name': 'guacapy',
    'version': '0.11.0',
    'description': 'REST API client for Apache Guacamole',
    'long_description': '# Guacamole REST API bindings for Python\n\n![PyPI](https://img.shields.io/pypi/v/guacapy)\n![PyPI - Downloads](https://img.shields.io/pypi/dm/guacapy)\n![PyPI - License](https://img.shields.io/pypi/l/guacapy)\n![Python Lint](https://github.com/pschmitt/guacapy/workflows/Python%20Lint/badge.svg)\n',
    'author': 'Philipp Schmitt',
    'author_email': 'philipp@schmitt.co',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6',
}


setup(**setup_kwargs)
