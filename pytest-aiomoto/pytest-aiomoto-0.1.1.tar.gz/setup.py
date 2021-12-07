# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pytest_aiomoto']

package_data = \
{'': ['*']}

install_requires = \
['aiobotocore[boto3]>=2.0.0,<3.0.0',
 'aiofiles>=0.7.0,<0.8.0',
 'moto[server,all]>=2.0.0,<3.0.0',
 'pytest-asyncio>=0.14.0,<0.15.0',
 'pytest>=6.2.5,<7.0.0',
 'requests>=2.23.0,<3.0.0']

entry_points = \
{'pytest11': ['aiomoto = pytest_aiomoto.plugin']}

setup_kwargs = {
    'name': 'pytest-aiomoto',
    'version': '0.1.1',
    'description': 'pytest-aiomoto',
    'long_description': '# pytest-aiomoto\n\n[![Documentation Status](https://readthedocs.org/projects/pytest-aiomoto/badge/?version=latest)](https://pytest-aiomoto.readthedocs.io/en/latest/?badge=latest)\n\n[![PyPI version](https://img.shields.io/pypi/v/pytest-aiomoto.svg)](https://pypi.org/project/pytest-aiomoto)\n[![Python versions](https://img.shields.io/pypi/pyversions/pytest-aiomoto.svg)](https://pypi.org/project/pytest-aiomoto)\n\n[pytest](https://docs.pytest.org) fixtures for AWS services,\nwith support for asyncio fixtures using\n[aiobotocore](https://aiobotocore.readthedocs.io)\n\n## Warning\n\n- This package is work in progress, it is not recommended for production purposes.\n  During the initial phases of this project, it is likely that some releases\n  could introduce breaking changes in test fixtures.  It\'s highly\n  recommended pinning this dependency to patch releases during the\n  0.x.y releases.\n- This package could restrict available versions of aws libs, including:\n  aiobotocore, botocore, boto3, and moto.  The initial intention is to allow\n  any 2.x.y versions of aiobotocore and moto.\n- The fixtures in this package might not be optimized for concurrent testing.\n  It is not known yet whether the fixtures are thread safe or adequately\n  randomized to support parallel test suites.\n\n## Installation\n\nYou can install "pytest-aiomoto" via pip\n\n    $ pip install pytest-aiomoto\n\n## Usage\n\nTo list the available fixtures\n\n    $ pytest --fixtures\n\nThis project attempts to provide some common fixtures for commonly used\nservices.  As such, it is not a generic package for any services; the\nmoto project provides that and this project builds on that.  This\nproject aims to create some useful fixtures that behave nearly the\nsame way for both synchronous clients (botocore) and\nasynchronous clients (aiobotocore).\n\n## Contributing\n\nContributions are welcome, if you build similar common fixtures or build\non the existing package fixtures.  The details for bug fixes could be\ncomplicated, due to the dependencies on aiobotocore and moto.\n\nPlease review [github collaboration](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests)\npractices.  Once you clone your fork of the repository:\n\n    cd pytest-aiomoto\n    make init\n    make test\n\nIt\'s recommended that development use python 3.7, to avoid introducing any python\ncode that might not be compatible with the minimum version of python supported.  This\nis important in the context of the general evolution of asyncio in python.\n\nMost development is done in a linux context (e.g. Ubuntu LTS).  If some development\ntools or common practices are not working as expected on OSX or Windows, there is\nlimited support for adapting to various development environments.\n\nTests are run with [pytest](https://github.com/pytest-dev/pytest), please ensure\nthe percentage of coverage at least stays the same before you submit a pull request.\nThe expectation for contributions might be a slow process, please do not anticipate\nany turn around on the order of days (unless you\'re already a core contributor).\nUsing your own fork can be a faster way to evolve your fixtures for your use cases.\n\n## Issues\n\nIf you encounter any problems, please\n[file an issue](https://github.com/dazza-codes/pytest-aiomoto/issues)\nalong with a detailed description.\n\n# License\n\nDistributed under the terms of the\n[Apache Software License 2.0](http://www.apache.org/licenses/LICENSE-2.0),\n"pytest-aiomoto" is free and open source software.\n\n```text\nCopyright 2021 Darren Weber\n\nLicensed under the Apache License, Version 2.0 (the "License");\nyou may not use this file except in compliance with the License.\nYou may obtain a copy of the License at\n\n   http://www.apache.org/licenses/LICENSE-2.0\n\nUnless required by applicable law or agreed to in writing, software\ndistributed under the License is distributed on an "AS IS" BASIS,\nWITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.\nSee the License for the specific language governing permissions and\nlimitations under the License.\n```\n\n# Notices\n\nInspiration for this project comes from testing the\n[aio-aws](https://github.com/dazza-codes/aio-aws) project,\nwhich uses the Apache 2 license.\n',
    'author': 'Darren Weber',
    'author_email': 'dazza-codes@github.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/dazza-codes/pytest-aiomoto',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
