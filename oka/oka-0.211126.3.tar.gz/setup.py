# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['oka']

package_data = \
{'': ['*']}

install_requires = \
['idict>=1.211127.3,<2.0.0',
 'pandas>=1.3.4,<2.0.0',
 'python-dotenv>=0.19.2,<0.20.0',
 'requests>=2.26.0,<3.0.0',
 'sklearn>=0.0,<0.1']

setup_kwargs = {
    'name': 'oka',
    'version': '0.211126.3',
    'description': 'Python client for oka repository',
    'long_description': None,
    'author': 'Rafael Bizao',
    'author_email': 'rabizao@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
