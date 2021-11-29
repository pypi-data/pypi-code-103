# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pyvultr', 'pyvultr.utils', 'pyvultr.v2']

package_data = \
{'': ['*']}

install_requires = \
['dacite>=1.6.0,<2.0.0', 'requests>=2.26.0,<3.0.0']

setup_kwargs = {
    'name': 'pyvultr',
    'version': '0.1.0',
    'description': 'Python library for Vultr API',
    'long_description': None,
    'author': 'fishermanadg',
    'author_email': 'fishermanadg@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6.2,<4.0.0',
}


setup(**setup_kwargs)
