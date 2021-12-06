# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['acestock']

package_data = \
{'': ['*']}

install_requires = \
['easytrader>=0.23.0,<0.24.0',
 'jotdx>=0.1.2,<0.2.0',
 'pandas>=1.3.4,<2.0.0',
 'tzlocal>=4.1,<5.0']

setup_kwargs = {
    'name': 'acestock',
    'version': '0.1.4',
    'description': 'A gateway for jonpy on A stock market.',
    'long_description': None,
    'author': 'FangyangJz',
    'author_email': 'fangyang.jing@hotmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7.1,<4.0.0',
}


setup(**setup_kwargs)
