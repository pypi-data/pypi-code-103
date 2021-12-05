# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['trendly', 'trendly.sources']

package_data = \
{'': ['*']}

install_requires = \
['searchtweets-v2>=1.1.1,<2.0.0']

setup_kwargs = {
    'name': 'trendly',
    'version': '0.1.0',
    'description': 'Real time trend analysis',
    'long_description': None,
    'author': 'jonirap',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
