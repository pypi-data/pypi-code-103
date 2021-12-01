# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['clear_s2s']

package_data = \
{'': ['*'], 'clear_s2s': ['CLEAR/templates/*']}

install_requires = \
['Django>=2.2.6,<3.0.0',
 'Jinja2>=3.0.2,<4.0.0',
 'requests-pkcs12>=1.13,<2.0',
 'xmltodict>=0.12.0,<0.13.0']

setup_kwargs = {
    'name': 'clear-s2s',
    'version': '0.1.6',
    'description': '',
    'long_description': None,
    'author': 'Your Name',
    'author_email': 'you@example.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
