# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['bitmex_async_rest']

package_data = \
{'': ['*']}

install_requires = \
['anyio>=2.0.2,<3.0.0', 'asks>=2.4.12,<3.0.0', 'orjson>=3.6.4,<4.0.0']

setup_kwargs = {
    'name': 'bitmex-async-rest',
    'version': '0.7.0',
    'description': 'Async REST Api wrapper for BitMEX cryptocurrency derivatives exchange.',
    'long_description': '# BitMEX Async-Rest\n\n\n[![PyPI](https://img.shields.io/pypi/v/bitmex_async_rest.svg)](https://pypi.python.org/pypi/bitmex-async-rest)\n[![Build Status](https://img.shields.io/travis/com/andersea/bitmex-async-rest.svg)](https://travis-ci.com/andersea/bitmex-async-rest)\n\nAsync Rest API implementation for BitMEX cryptocurrency derivatives exchange.\n\n* Free software: MIT license\n\n## Features\n\n* Supports authenticated connections using api keys.\n* Based on asks and anyio. Should work on all anyio supported event loops.\n\n## Non-features\n\n* This is a beta api. Methods are probably named badly and a lot of stuff you might want is missing.\n\n## Installation\n\nThis library requires Python 3.7 or greater. \n\nTo install from PyPI:\n\n    pip install bitmex-async-rest\n\n## Client example\n\nTODO\n\n## API\n\nRead the source code. (Welp..)\n\nThis library does not do retrys. If you get overload or similar errors, it is up to the client to handle them.\n\n## Credits\n\nThanks to the [Trio](https://github.com/python-trio/trio), [Curio](https://github.com/dabeaz/curio), [AnyIO] (https://github.com/agronholm/anyio) and [asks](https://github.com/theelous3/asks) libraries for their awesome work.\n',
    'author': 'Anders Ellenshøj Andersen',
    'author_email': 'andersa@ellenshoej.dk',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/andersea/bitmex-async-rest',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
