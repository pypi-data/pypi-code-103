# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['storage',
 'storage.common',
 'storage.common.cache',
 'storage.common.utils',
 'storage.config',
 'storage.model',
 'storage.mongo',
 'storage.mysql',
 'storage.oracle',
 'storage.storage',
 'storage.storage.exception',
 'storage.storage.utils']

package_data = \
{'': ['*']}

install_requires = \
['SQLAlchemy>=1.4.27,<2.0.0',
 'arrow>=1.1.0,<2.0.0',
 'cacheout>=0.13.1,<0.14.0',
 'cx-Oracle>=8.2.1,<9.0.0',
 'mysqlclient>=2.1.0,<3.0.0',
 'pydantic>=1.8.2,<2.0.0',
 'pymongo>=3.11.4,<4.0.0']

setup_kwargs = {
    'name': 'watchmen-storage-engine',
    'version': '0.1.16',
    'description': '',
    'long_description': None,
    'author': 'luke0623',
    'author_email': 'luke0623@outlook.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
