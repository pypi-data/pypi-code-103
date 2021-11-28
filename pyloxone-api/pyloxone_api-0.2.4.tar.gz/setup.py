# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pyloxone_api']

package_data = \
{'': ['*']}

install_requires = \
['httpx>=0.19.0,<0.20.0',
 'pycryptodome>=3.10.1,<4.0.0',
 'websockets>=9.0.1,<10.0.0']

setup_kwargs = {
    'name': 'pyloxone-api',
    'version': '0.2.4',
    'description': 'A package for interacting at a low(ish) level with a Loxone miniserver via the Loxone websocket API',
    'long_description': 'Pyloxone-api\n============\n\nA Python API for communicating with a [Loxone](http://www.loxone.com)\nminiserver.\n\xa0\n\xa0\n\n![PyPI - Python Version](https://img.shields.io/pypi/pyversions/pyloxone-api?style=flat-square)\n![PyPI - License](https://img.shields.io/pypi/l/pyloxone-api?style=flat-square)\n[![PyPI](https://img.shields.io/pypi/v/pyloxone-api?style=flat-square)](https://pypi.python.org/pypi/pyloxone-api/)\n\xa0\n\xa0\n\xa0\n\nDevelopment\n===========\n\nWe use [Poetry](https://python-poetry) for package and environment management,\n[Black](https://pypi.org/project/black/) and [isort](https://pypi.org/project/isort/)\nfor code formatting, and [Pytest](https://pytest.org) for testing.\n\n* Install [Poetry](https://python-poetry)\n\n* Clone the project from Github, and use `Poetry` to install a virtual\n  environment and all dependencies:\n    ```shell\n    > git clone https://github.com/jodehli/pyloxone-api\n    > cd pyloxone-api\n    > poetry install\n    ```\n\n* Activate the virtual environment and create a shell:\n    ```shell\n    > poetry shell\n    ```\n\n* To test, make sure the virtual environment is activiated, and run `pytest`:\n    ```shell\n    > pytest\n    ```\n\n* There are some tests which require a live miniserver on the network. They are\n  slower, and are not run by default. Be careful with these tests—they might\n  make your miniserver behave oddly. To run them, you must specify appropriate\ncredentials, eg:\n\n  ```bash\n  > pytest --host=192.168.1.100 --port=80  --username=admin --password=admin\n  ```\n',
    'author': 'Joachim Dehli',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/JoDehli/pyloxone-api',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
