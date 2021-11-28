# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['demapi', 'demapi.configure', 'demapi.connector']

package_data = \
{'': ['*']}

install_requires = \
['aiohttp>=3.8.1,<4.0.0',
 'certifi>=2021.10.8,<2022.0.0',
 'requests>=2.26.0,<3.0.0']

extras_require = \
{'check': ['mypy>=0.910,<0.911',
           'types-requests>=2.26.1,<3.0.0',
           'types-certifi>=2021.10.8,<2022.0.0'],
 'style': ['black>=21.11b1,<22.0',
           'isort>=5.10.1,<6.0.0',
           'pre-commit>=2.15.0,<3.0.0'],
 'test': ['pytest-cov>=3.0.0,<4.0.0',
          'coveralls>=3.3.1,<4.0.0',
          'coverage>=6.1.2,<7.0.0',
          'pytest-asyncio>=0.16.0,<0.17.0',
          'pytest>=6.2.5,<7.0.0']}

setup_kwargs = {
    'name': 'demapi',
    'version': '0.1.5',
    'description': 'Make customizable demotivators and motivators through imgonline.com.ua API. Supports async-await style',
    'long_description': '# DemAPI\n> Make customizable demotivators and motivators through imgonline.com.ua API. Supports async-await style\n\n![Example](https://raw.githubusercontent.com/deknowny/demapi/main/assets/example.png)\n***\n__Documentation__: Check out [GUIDE.md](https://github.com/deknowny/demapi/blob/main/GUIDE.md)\n\n[![Coverage Status](https://coveralls.io/repos/github/deknowny/demapi/badge.svg?branch=main)](https://coveralls.io/github/deknowny/demapi?branch=main)\n![PyPI - Python Version](https://img.shields.io/pypi/pyversions/demapi)\n![PyPI - Downloads](https://img.shields.io/pypi/dm/demapi)\n![PyPI](https://img.shields.io/pypi/v/demapi)\n![PyPI - Implementation](https://img.shields.io/pypi/implementation/demapi)\n\n# Features\n* Sync and `async-await` style\n* Customizable titles and explanation (size, colors etc.)\n* Flexible output image (line breaks showed correctly)\n* Not CPU-bound (through unlimited API)\n* Full tests coverage\n* Full typed\n\n## Overview\nConfigure request params such as text, color, size etc.\nAnd then download the image. Optionally save to disk otherwise\nuse `image.content` for raw bytes object\n```python\nimport demapi\n\n\nconf = demapi.Configure(\n    base_photo="example.png",\n    title="The first line",\n    explanation="The second line"\n)\nimage = conf.download()\nimage.save("example.png")\n```\n\nOr via `await` (based on `aiohttp`):\n\n```python\nimage = await conf.coroutine_download()\n```\n\n# Installation\nInstall the latest version through `GitHub`:\n```shell\npython -m pip install https://github.com/deknowny/demapi/archive/main.zip\n```\nOr through `PyPI`\n```shell\npython -m pip install demapi\n```\n\n# Contributing\nCheck out [CONTRIBUTING.md](./CONTRIBUTING.md)\n\n',
    'author': 'Yan Kurbatov',
    'author_email': 'deknowny@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/deknowny/demapi',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
