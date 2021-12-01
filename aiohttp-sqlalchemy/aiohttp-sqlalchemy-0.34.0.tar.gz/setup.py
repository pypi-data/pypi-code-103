# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['aiohttp_sqlalchemy']

package_data = \
{'': ['*']}

install_requires = \
['SQLAlchemy>=1.4.22,<2.0.0',
 'aiohttp-things>=0.13.0',
 'aiohttp>=3.7.4.post0,<4.0.0',
 'sqlalchemy-things>=0.10.1']

extras_require = \
{'mysql': ['aiomysql>=0.0.22'],
 'postgresql': ['asyncpg>=0.25.0'],
 'sqlite': ['aiosqlite>=0.17.0']}

setup_kwargs = {
    'name': 'aiohttp-sqlalchemy',
    'version': '0.34.0',
    'description': 'SQLAlchemy 1.4 / 2.0 support for aiohttp.',
    'long_description': "==================\naiohttp-sqlalchemy\n==================\n|ReadTheDocs| |PyPI release| |PyPI downloads| |Python versions| |License| |GitHub CI| |Codecov| |Codacy|\n\n.. |ReadTheDocs| image:: https://readthedocs.org/projects/aiohttp-sqlalchemy/badge/?version=latest\n  :target: https://aiohttp-sqlalchemy.readthedocs.io/en/latest/?badge=latest\n  :alt: Read The Docs build\n\n.. |PyPI release| image:: https://badge.fury.io/py/aiohttp-sqlalchemy.svg\n  :target: https://pypi.org/project/aiohttp-sqlalchemy/\n  :alt: Release\n\n.. |PyPI downloads| image:: https://static.pepy.tech/personalized-badge/aiohttp-sqlalchemy?period=total&units=international_system&left_color=grey&right_color=blue&left_text=Downloads\n  :target: https://pepy.tech/project/aiohttp-sqlalchemy\n  :alt: PyPI downloads count\n\n.. |Python versions| image:: https://img.shields.io/badge/Python-3.7%20%7C%203.8%20%7C%203.9%20%7C%203.10-blue\n  :target: https://pypi.org/project/aiohttp-sqlalchemy/\n  :alt: Python version support\n\n.. |License| image:: https://img.shields.io/badge/License-MIT-green\n  :target: https://github.com/ri-gilfanov/aiohttp-sqlalchemy/blob/master/LICENSE\n  :alt: MIT License\n\n.. |GitHub CI| image:: https://github.com/ri-gilfanov/aiohttp-sqlalchemy/actions/workflows/ci.yml/badge.svg?branch=master\n  :target: https://github.com/ri-gilfanov/aiohttp-sqlalchemy/actions/workflows/ci.yml\n  :alt: GitHub continuous integration\n\n.. |Codecov| image:: https://codecov.io/gh/ri-gilfanov/aiohttp-sqlalchemy/branch/master/graph/badge.svg\n  :target: https://codecov.io/gh/ri-gilfanov/aiohttp-sqlalchemy\n  :alt: codecov.io status for master branch\n\n.. |Codacy| image:: https://app.codacy.com/project/badge/Grade/19d5c531ed75435988ba8dc91031514c\n  :target: https://www.codacy.com/gh/ri-gilfanov/aiohttp-sqlalchemy/dashboard?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=ri-gilfanov/aiohttp-sqlalchemy&amp;utm_campaign=Badge_Grade\n   :alt: Codacy code quality\n\n`SQLAlchemy 1.4 / 2.0 <https://www.sqlalchemy.org/>`_ support for `AIOHTTP\n<https://docs.aiohttp.org/>`_.\n\nThe library provides the next features:\n\n* initializing asynchronous sessions through a middlewares;\n* initializing asynchronous sessions through a decorators;\n* simple access to one asynchronous session by default key;\n* preventing attributes from being expired after commit by default;\n* support different types of request handlers;\n* support nested applications.\n\n\nDocumentation\n-------------\nhttps://aiohttp-sqlalchemy.readthedocs.io\n\n\nInstallation\n------------\n::\n\n    pip install aiohttp-sqlalchemy\n\n\nSimple example\n--------------\nInstall ``aiosqlite`` for work with sqlite3: ::\n\n  pip install aiosqlite\n\nCopy and paste this code in a file and run:\n\n.. code-block:: python\n\n  from datetime import datetime\n\n  import sqlalchemy as sa\n  from aiohttp import web\n  from sqlalchemy import orm\n\n  import aiohttp_sqlalchemy as ahsa\n\n  metadata = sa.MetaData()\n  Base = orm.declarative_base(metadata=metadata)\n\n\n  class MyModel(Base):\n      __tablename__ = 'my_table'\n\n      pk = sa.Column(sa.Integer, primary_key=True)\n      timestamp = sa.Column(sa.DateTime(), default=datetime.now)\n\n\n  async def main(request):\n      sa_session = ahsa.get_session(request)\n\n      async with sa_session.begin():\n          sa_session.add(MyModel())\n          result = await sa_session.execute(sa.select(MyModel))\n          result = result.scalars()\n\n      data = {\n          instance.pk: instance.timestamp.isoformat()\n          for instance in result\n      }\n      return web.json_response(data)\n\n\n  async def app_factory():\n      app = web.Application()\n\n      ahsa.setup(app, [\n          ahsa.bind('sqlite+aiosqlite:///'),\n      ])\n      await ahsa.init_db(app, metadata)\n\n      app.add_routes([web.get('/', main)])\n      return app\n\n\n  if __name__ == '__main__':\n      web.run_app(app_factory())\n",
    'author': 'Ruslan Ilyasovich Gilfanov',
    'author_email': 'ri.gilfanov@yandex.ru',
    'maintainer': 'Ruslan Ilyasovich Gilfanov',
    'maintainer_email': 'ri.gilfanov@yandex.ru',
    'url': 'https://pypi.org/project/aiohttp-sqlalchemy/',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
