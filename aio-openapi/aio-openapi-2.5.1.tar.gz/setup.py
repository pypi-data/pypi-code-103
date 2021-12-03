# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['openapi',
 'openapi.data',
 'openapi.db',
 'openapi.db.openapi',
 'openapi.spec',
 'openapi.ws']

package_data = \
{'': ['*']}

install_requires = \
['PyYAML>=6.0,<7.0',
 'SQLAlchemy-Utils>=0.37.9,<0.38.0',
 'SQLAlchemy>=1.4.27,<2.0.0',
 'aiohttp>=3.8.0,<4.0.0',
 'alembic',
 'asyncpg>=0.24.0,<0.25.0',
 'click>=8.0.3,<9.0.0',
 'email-validator>=1.1.3,<2.0.0',
 'httptools>=0.3.0,<0.4.0',
 'psycopg2-binary>=2.9.2,<3.0.0',
 'python-dateutil>=2.8.2,<3.0.0',
 'pytz>=2021.3,<2022.0',
 'simplejson>=3.17.5,<4.0.0',
 'uvloop>=0.16.0,<0.17.0']

extras_require = \
{'dev': ['aiodns>=3.0.0,<4.0.0',
         'PyJWT>=2.3.0,<3.0.0',
         'colorlog>=6.6.0,<7.0.0',
         'phonenumbers>=8.12.37,<9.0.0',
         'cchardet>=2.1.7,<3.0.0'],
 'docs': ['Sphinx>=4.3.0,<5.0.0',
          'sphinx-copybutton>=0.4.0,<0.5.0',
          'sphinx-autodoc-typehints>=1.12.0,<2.0.0',
          'aiohttp-theme>=0.1.6,<0.2.0',
          'recommonmark>=0.7.1,<0.8.0']}

setup_kwargs = {
    'name': 'aio-openapi',
    'version': '2.5.1',
    'description': 'Minimal OpenAPI asynchronous server application',
    'long_description': '# aio-openapi\n\n[![PyPI version](https://badge.fury.io/py/aio-openapi.svg)](https://badge.fury.io/py/aio-openapi)\n[![Python versions](https://img.shields.io/pypi/pyversions/aio-openapi.svg)](https://pypi.org/project/aio-openapi)\n[![Build](https://github.com/quantmind/aio-openapi/workflows/build/badge.svg)](https://github.com/quantmind/aio-openapi/actions?query=workflow%3Abuild)\n[![Coverage Status](https://coveralls.io/repos/github/quantmind/aio-openapi/badge.svg?branch=master)](https://coveralls.io/github/quantmind/aio-openapi?branch=master)\n[![Documentation Status](https://readthedocs.org/projects/aio-openapi/badge/?version=latest)](https://aio-openapi.readthedocs.io/en/latest/?badge=latest)\n[![Downloads](https://img.shields.io/pypi/dd/aio-openapi.svg)](https://pypi.org/project/aio-openapi/)\n\nAsynchronous web middleware for [aiohttp][] and serving Rest APIs with [OpenAPI][] v 3\nspecification and with optional [PostgreSql][] database bindings.\n\n<!-- START doctoc generated TOC please keep comment here to allow auto update -->\n<!-- DON\'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->\n\n**Table of Contents**\n\n- [Installation](#installation)\n- [Development](#development)\n- [Features](#features)\n- [Web App](#web-app)\n- [OpenAPI Documentation](#openapi-documentation)\n- [Database Integration](#database-integration)\n- [Websockets](#websockets)\n  - [RPC protocol](#rpc-protocol)\n  - [Publish/Subscribe](#publishsubscribe)\n- [Environment Variables](#environment-variables)\n\n<!-- END doctoc generated TOC please keep comment here to allow auto update -->\n\n## Installation\n\n```\npip install aio-openapi\n```\n\n## Development\n\nClone the repository and create a virtual environment `venv`.\n\nInstall dependencies by running the install script\n\n```\nmake install\n```\n\nTo run tests\n\n```\nmake test\n```\n\nBy default tests are run against a database with the following connection string `postgresql+asyncpg://postgres:postgres@localhost:5432/openapi`. To use a different DB, create a `.env` file with\na different connection string, for example:\n\n```\nDATASTORE=postgresql+asyncpg://postgres:postgres@localhost:6432/openapi\n```\n\n## Features\n\n- Asynchronous web routes with [aiohttp](https://aiohttp.readthedocs.io/en/stable/)\n- Data validation, serialization and unserialization with python [dataclasses](https://docs.python.org/3/library/dataclasses.html)\n- [OpenApi][] v 3 auto documentation\n- [SqlAlchemy][] expression language\n- Asynchronous DB interaction with [asyncpg][]\n- Migrations with [alembic][]\n- SqlAlchemy tables as python dataclasses\n- Support [click][] command line interface\n- Optional [sentry](https://sentry.io) middleware\n\n## Web App\n\nTo create an openapi RESTful application follow this schema (lets call the file `main.py`)\n\n```python\nfrom openapi.rest import rest\n\ndef create_app():\n    return rest(\n        openapi=dict(\n            title=\'A REST API\',\n            ...\n        ),\n        base_path=\'/v1\',\n        allowed_tags=[...],\n        validate_docs=True,\n        setup_app=setup_app,\n        commands=[...]\n    )\n\n\ndef setup_app(app):\n    app.router.add_routes(...)\n    return app\n\n\nif __name__ == \'__main__\':\n    create_app().main()\n```\n\nThe `create_app` function creates the [aiohttp][] server application by invoking the `rest` function.\nThis function adds the [click][] command in the `cli` mapping entry and add\ndocumentation for routes which support OpenAPI docs.\nThe `setup_app` function is used to actually setup the custom application, usually by adding middleware, routes,\nshutdown callbacks, database integration and so forth.\n\n## OpenAPI Documentation\n\nThe library provide tools for creating OpenAPI v 3 compliant endpoints and\nauto-document them.\n\nAn example from test `tests/example` directory\n\n```python\nfrom typing import List\n\nfrom aiohttp import web\n\nfrom openapi.db.path import SqlApiPath\nfrom openapi.spec import op\n\n\nroutes = web.RouteTableDef()\n\n\n@routes.view(\'/tasks\')\nclass TasksPath(SqlApiPath):\n    """\n    ---\n    summary: Create and query Tasks\n    tags:\n        - name: Task\n          description: Task tag description\n    """\n    table = \'tasks\'\n\n    @op(query_schema=TaskOrderableQuery, response_schema=List[Task])\n    async def get(self) -> web.Response:\n        """\n        ---\n        summary: Retrieve Tasks\n        description: Retrieve a list of Tasks\n        responses:\n            200:\n                description: Authenticated tasks\n        """\n        paginated = await self.get_list()\n        return paginated.json_response()\n\n    @op(response_schema=Task, body_schema=TaskAdd)\n    async def post(self) -> web.Response:\n        """\n        ---\n        summary: Create a Task\n        description: Create a new Task\n        responses:\n            201:\n                description: the task was successfully added\n            422:\n                description: Failed validation\n        """\n        data = await self.create_one()\n        return self.json_response(data, status=201)\n```\n\n## Database Integration\n\nThis library provides integration with [asyncpg][], an high performant asynchronous\nconnector with [PostgreSql][] database.\nTo add the database extension simply use the `get_db` function in the applicatiuon `setup_app` function:\n\n```python\nfrom aiohttp import web\n\nfrom openapi.db import get_db\n\ndef setup_app(app: web.Application) -> None:\n    db = get_db(app)\n    meta = db.metadata\n\n```\n\nThis will enable database connection and command line tools (most of them from [alembic][]):\n\n```\npython main.py db --help\n```\n\nThe database container is available at the `db` app key:\n\n```python\napp[\'db\']\n```\n\n## Environment Variables\n\nSeveral environment variables are used by the library to support testing and deployment.\n\n- `DATASTORE`: PostgreSql connection string (same as [SqlAlchemy][] syntax)\n- `DBPOOL_MIN_SIZE`: minimum size of database connection pool (default is 10)\n- `DBPOOL_MAX_SIZE`: maximum size of database connection pool (default is 10)\n\n[aiohttp]: https://aiohttp.readthedocs.io/en/stable/\n[openapi]: https://www.openapis.org/\n[postgresql]: https://www.postgresql.org/\n[sqlalchemy]: https://www.sqlalchemy.org/\n[click]: https://github.com/pallets/click\n[alembic]: http://alembic.zzzcomputing.com/en/latest/\n[asyncpg]: https://github.com/MagicStack/asyncpg\n',
    'author': 'Luca',
    'author_email': 'luca@quantmind.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/quantmind/aio-openapi',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
