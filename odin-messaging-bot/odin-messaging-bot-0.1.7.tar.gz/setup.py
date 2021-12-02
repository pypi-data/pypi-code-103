# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['odin_messaging_bot']

package_data = \
{'': ['*']}

install_requires = \
['aiohttp>=3.3.1,<4.0.0',
 'asyncio-nats-streaming>=0.4.0,<0.5.0',
 'nats-py>=2.0.0-rc.3,<3.0.0',
 'nest-asyncio>=1.5.1,<2.0.0',
 'pydantic>=1.8.2,<2.0.0',
 'python-dotenv>=0.19.1,<0.20.0',
 'ujson>=4.3.0,<5.0.0']

setup_kwargs = {
    'name': 'odin-messaging-bot',
    'version': '0.1.7',
    'description': 'A NATS/STAN Bot to publish/subscribe messages.',
    'long_description': None,
    'author': 'adolfrodeno',
    'author_email': 'amvillalobos@uc.cl',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
