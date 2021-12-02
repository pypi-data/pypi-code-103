# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['redisai']

package_data = \
{'': ['*']}

install_requires = \
['Deprecated>=1.2.12,<2.0.0',
 'hiredis>=0.20',
 'numpy>=1.19.5',
 'redis==3.5.3',
 'six>=1.10.0']

setup_kwargs = {
    'name': 'redisai',
    'version': '1.2.2',
    'description': 'RedisAI Python Client',
    'long_description': "==========\nredisai-py\n==========\n\n.. image:: https://img.shields.io/github/license/RedisAI/redisai-py.svg\n        :target: https://github.com/RedisAI/redisai-py\n\n.. image:: https://badge.fury.io/py/redisai.svg\n        :target: https://badge.fury.io/py/redisai\n\n.. image:: https://circleci.com/gh/RedisAI/redisai-py/tree/master.svg?style=svg\n        :target: https://circleci.com/gh/RedisAI/redisai-py/tree/master\n\n.. image:: https://img.shields.io/github/release/RedisAI/redisai-py.svg\n        :target: https://github.com/RedisAI/redisai-py/releases/latest\n\n.. image:: https://codecov.io/gh/RedisAI/redisai-py/branch/master/graph/badge.svg\n        :target: https://codecov.io/gh/RedisAI/redisai-py\n\n.. image:: https://readthedocs.org/projects/redisai-py/badge/?version=latest\n        :target: https://redisai-py.readthedocs.io/en/latest/?badge=latest\n\n.. image:: https://img.shields.io/badge/Forum-RedisAI-blue\n        :target: https://forum.redislabs.com/c/modules/redisai\n\n.. image:: https://img.shields.io/discord/697882427875393627?style=flat-square\n        :target: https://discord.gg/rTQm7UZ\n\n.. image:: https://snyk.io/test/github/RedisAI/redisai-py/badge.svg?targetFile=pyproject.toml)](https://snyk.io/test/github/RedisAI/redisai-py?targetFile=pyproject.toml\n\nredisai-py is the Python client for RedisAI. Checkout the\n`documentation <https://redisai-py.readthedocs.io/en/latest/>`_ for API details and examples\n\nInstallation\n------------\n\n1. Install Redis 5.0 or above\n2. Install `RedisAI <http://redisai.io>`_\n3. Install the Python client\n\n.. code-block:: bash\n\n    $ pip install redisai\n\n\n4. Install serialization-deserialization utility (optional)\n\n.. code-block:: bash\n\n    $ pip install ml2rt\n\nDevelopment\n-----------\n\n1. Assuming you have virtualenv installed, create a virtualenv to manage your python dependencies, and activate it.\n   ```virtualenv -v venv; source venv/bin/activate```\n2. Install [pypoetry](https://python-poetry.org/) to manage your dependencies.\n   ```pip install poetry```\n3. Install dependencies.\n   ```poetry install --no-root```\n\n[tox](https://tox.readthedocs.io/en/latest/) runs all tests as its default target. Running *tox* by itself will run unit tests. Ensure you have a running redis, with the module loaded.\n\n**Contributing**\n\nPrior to submitting a pull request, please ensure you've built and installed poetry as above. Then:\n\n1. Run the linter.\n   ```tox -e linters.```\n2. Run the unit tests. This assumes you have a redis server running, with the [RedisAI module](https://redisai.io) already loaded.  If you don't, you may want to install a [docker build](https://hub.docker.com/r/redislabs/redisai/tags).\n   ```tox -e tests```\n\n`RedisAI example repo <https://github.com/RedisAI/redisai-examples>`_ shows few examples\nmade using redisai-py under `python_client` folder. Also, checkout\n`ml2rt <https://github.com/hhsecond/ml2rt>`_ for convenient functions those might help in\nconverting models (sparkml, sklearn, xgboost to ONNX), serializing models to disk, loading\nit back to redisai-py etc.\n",
    'author': 'RedisLabs',
    'author_email': 'oss@redislabs.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<3.10',
}


setup(**setup_kwargs)
