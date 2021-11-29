# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['ipapp',
 'ipapp.asgi',
 'ipapp.db',
 'ipapp.http',
 'ipapp.logger',
 'ipapp.logger.adapters',
 'ipapp.mq',
 'ipapp.openapi',
 'ipapp.rpc',
 'ipapp.rpc.http',
 'ipapp.rpc.jsonrpc',
 'ipapp.rpc.jsonrpc.http',
 'ipapp.rpc.jsonrpc.mq',
 'ipapp.rpc.jsonrpc.openrpc',
 'ipapp.rpc.mq',
 'ipapp.rpc.restrpc',
 'ipapp.rpc.restrpc.http',
 'ipapp.rpc.restrpc.openapi',
 'ipapp.s3',
 'ipapp.sftp',
 'ipapp.sphinx',
 'ipapp.task',
 'ipapp.utils',
 'ipapp.utils.lock']

package_data = \
{'': ['*']}

install_requires = \
['aiohttp>=3.6.2,<4.0.0',
 'aiojobs>=1.0.0,<2.0.0',
 'aiozipkin>=0.7,<1.2',
 'async-timeout>=4.0.0,<5.0.0',
 'deepmerge>=0.2.1,<0.4.0',
 'docstring-parser>=0.7.1,<0.9.0',
 'jsonschema>=3.2.0,<4.0.0',
 'prometheus-client>=0.8,<0.12',
 'pydantic>=1.8.2,<2.0.0',
 'pyyaml>=5.4,<6.0',
 'sentry-sdk>=1.0.0,<2.0.0',
 'tinyrpc>=1.0.4,<2.0.0']

extras_require = \
{'dbtm': ['asyncpg>=0.22,<0.24', 'crontab>=0.22.6,<0.24.0'],
 'fastapi': ['uvicorn>=0.12.1,<0.16.0', 'fastapi>=0.61,<0.69'],
 'oracle': ['cx-Oracle>=8.0.0,<9.0.0'],
 'postgres': ['asyncpg>=0.22,<0.24'],
 'rabbitmq': ['pika>=1.2.0,<2.0.0'],
 'redis': ['aioredis>=1.3.1,<2.0.0'],
 's3': ['aiobotocore>=1.2.2,<2.0.0', 'python-magic>=0.4.22,<0.5.0'],
 'sftp': ['asyncssh[pyOpenSSL]>=2.3.0,<3.0.0'],
 'testing': ['black==21.9b0',
             'flake8==3.9.2',
             'mock>=4.0.2,<5.0.0',
             'mypy==0.812',
             'bandit==1.6.3',
             'isort==5.9.3',
             'safety>=1.10.3,<2.0.0',
             'pylint>=2.7.2,<3.0.0',
             'pytest-aiohttp>=0.3.0,<0.4.0',
             'pytest>=6.1.0,<7.0.0',
             'pytest-asyncio>=0.14.0,<0.15.0',
             'pytest-cov>=2.11.0,<3.0.0',
             'coverage[toml]>=5.3,<6.0',
             'Sphinx>=3.5.2,<5.0.0',
             'sphinx-rtd-theme>=0.5.1,<0.6.0',
             'tox>=3.23.0,<4.0.0',
             'docker-compose>=1.27.4,<2.0.0',
             'watchdog>=2.0.2,<3.0.0']}

setup_kwargs = {
    'name': 'ipapp',
    'version': '1.3.5',
    'description': 'InPlat application framework',
    'long_description': "# InPlat application framework\n> Framework with asyncio based on python.\n\n![PyPI](https://img.shields.io/pypi/v/ipapp?style=for-the-badge) ![PyPI - Python Version](https://img.shields.io/pypi/pyversions/ipapp?style=for-the-badge) ![Read the Docs](https://img.shields.io/readthedocs/ipapp?style=for-the-badge)\n\n## Documentation\nDocumentation can be found at [readthedocs](https://ipapp.readthedocs.io/ru/latest/).\n\n## Installation\nUsing pip:\n```sh\npip install ipapp\n```\nUsing poetry:\n```sh\npoetry add ipapp\n```\nInstallation with all dependencies: \n```sh\npoetry add ipapp[fastapi,oracle,postgres,rabbitmq,s3,sftp,dbtm,testing,redis]\n```\n\n## Usage example\nFor examples and usage, please refer to the [examples](examples) folder.\n\n## Release History\nFor release history refer to [release-notes](release-notes.rst).\n\n## Contributing\n1. Fork it\n2. Create your feature branch (`git checkout -b feature/fooBar`)\n3. Commit your changes (`git commit -am 'Add some fooBar'`)\n4. Push to the branch (`git push origin feature/fooBar`)\n5. Create a new Pull Request\n",
    'author': 'InPlat',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/inplat/ipapp',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
