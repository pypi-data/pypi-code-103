# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['kaeru']

package_data = \
{'': ['*']}

install_requires = \
['SQLAlchemy[asyncio]>=1.4.25,<2.0.0',
 'aiodns>=3.0.0,<4.0.0',
 'aiohttp>=3.7.4,<4.0.0',
 'aiosqlite>=0.17.0,<0.18.0',
 'cchardet>=2.1.7,<3.0.0']

entry_points = \
{'console_scripts': ['kaeru = kaeru.cli:run']}

setup_kwargs = {
    'name': 'kaeru',
    'version': '0.2.1',
    'description': '',
    'long_description': None,
    'author': 'faith',
    'author_email': 'jamienibtong@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
