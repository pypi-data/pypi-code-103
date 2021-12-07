# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['rmrk_tools', 'rmrk_tools.rmrk2_0_0']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'py-rmrk-tools',
    'version': '0.1.0a1',
    'description': '',
    'long_description': None,
    'author': 'Alisher A. Khassanov',
    'author_email': 'a.khssnv@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
