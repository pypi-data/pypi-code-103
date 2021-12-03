# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['desbrava_accounts',
 'desbrava_accounts.api',
 'desbrava_accounts.api.api_v1',
 'desbrava_accounts.api.api_v1.endpoints',
 'desbrava_accounts.constants',
 'desbrava_accounts.core',
 'desbrava_accounts.crud',
 'desbrava_accounts.db',
 'desbrava_accounts.models',
 'desbrava_accounts.schemas',
 'desbrava_accounts.tests',
 'desbrava_accounts.tests.api',
 'desbrava_accounts.tests.api.api_v1',
 'desbrava_accounts.tests.crud',
 'desbrava_accounts.tests.utils']

package_data = \
{'': ['*'], 'desbrava_accounts': ['email-templates/src/*']}

install_requires = \
['alembic>=1.4.2,<2.0.0',
 'celery>=4.4.2,<5.0.0',
 'email-validator>=1.0.5,<2.0.0',
 'emails>=0.5.15,<0.6.0',
 'fastapi>=0.70.0,<0.71.0',
 'gunicorn>=20.0.4,<21.0.0',
 'inflect>=5.3.0,<6.0.0',
 'jinja2>=2.11.2,<3.0.0',
 'passlib[bcrypt]>=1.7.2,<2.0.0',
 'psycopg2-binary>=2.8.5,<3.0.0',
 'pydantic>=1.4,<2.0',
 'pytest>=5.4.1,<6.0.0',
 'python-jose[cryptography]>=3.1.0,<4.0.0',
 'python-multipart>=0.0.5,<0.0.6',
 'raven>=6.10.0,<7.0.0',
 'requests>=2.23.0,<3.0.0',
 'sqlalchemy>=1.3.16,<2.0.0',
 'tenacity>=6.1.0,<7.0.0',
 'uvicorn>=0.11.3,<0.12.0']

setup_kwargs = {
    'name': 'desbrava-accounts',
    'version': '0.1.0',
    'description': '',
    'long_description': None,
    'author': 'Admin',
    'author_email': 'admin@example.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
