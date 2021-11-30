# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['bogmark',
 'bogmark.bases',
 'bogmark.logger',
 'bogmark.rabbitmq',
 'bogmark.server',
 'bogmark.server.middlewares',
 'bogmark.shared',
 'bogmark.structures',
 'bogmark.tests',
 'bogmark.tests.rabbitmq',
 'bogmark.tests.server',
 'bogmark.tests.server.simple_app',
 'bogmark.tests.server.simple_app.app',
 'bogmark.tests.server.simple_app.app.routers',
 'bogmark.tests.server.simple_app.app.routers.v1',
 'bogmark.tests.server.simple_app.app.routers.v1.handlers',
 'bogmark.tests.services',
 'bogmark.tests.services.api_user_settings',
 'bogmark.tests.services.api_users',
 'bogmark.tests.services.comments',
 'bogmark.tests.services.entities',
 'bogmark.tests.services.entity_user_token',
 'bogmark.tests.services.entity_users',
 'bogmark.tests.services.events',
 'bogmark.tests.services.file_saver',
 'bogmark.tests.services.mailboxes',
 'bogmark.tests.services.mailer',
 'bogmark.tests.services.payables',
 'bogmark.tests.services.reconciliation',
 'bogmark.tests.services.roles',
 'bogmark.tests.services.transactions',
 'bogmark.tests.structures']

package_data = \
{'': ['*']}

install_requires = \
['aiohttp-retry>=2.4.5,<3.0.0',
 'aiohttp[speedups]>=3.7.4,<4.0.0',
 'orjson>=3.6.1,<4.0.0',
 'pydantic[email]>=1.8.2,<2.0.0',
 'python-dotenv>=0.19.0,<0.20.0']

extras_require = \
{'all': ['fastapi>=0.68.0,<0.69.0',
         'starlette-prometheus>=0.7.0,<0.8.0',
         'pika>=1.2.0,<2.0.0',
         'aio-pika>=6.8.0,<7.0.0'],
 'rabbitmq': ['pika>=1.2.0,<2.0.0', 'aio-pika>=6.8.0,<7.0.0'],
 'server': ['fastapi>=0.68.0,<0.69.0', 'starlette-prometheus>=0.7.0,<0.8.0']}

setup_kwargs = {
    'name': 'bogmark',
    'version': '0.0.4',
    'description': '',
    'long_description': None,
    'author': 'Bogdan',
    'author_email': 'evstrat.bg@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
