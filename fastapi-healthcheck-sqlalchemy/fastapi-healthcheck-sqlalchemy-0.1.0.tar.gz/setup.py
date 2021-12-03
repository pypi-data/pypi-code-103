# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['fastapi_healthcheck_sqlalchemy']

package_data = \
{'': ['*']}

install_requires = \
['FastAPI-SQLAlchemy>=0.2.1,<0.3.0', 'fastapi-healthcheck>=0.2.2,<0.3.0']

setup_kwargs = {
    'name': 'fastapi-healthcheck-sqlalchemy',
    'version': '0.1.0',
    'description': 'A service to check the health of your applications SQLAlchemy connection.',
    'long_description': "# fastapi-healthcheck-sqlalchemy\n\nA module built on top of fastapi_healthcheck to check the status of your SQLAlchemy connection.  This requires a Table given to the health check so it can run a count of rows against it.  As long as it returns a value, the connection is alive.\n\n## Install\n\n`pip install fastapi-healthcheck-sqlalchemy` or `poetry add fastapi-healthcheck-sqlalchemy`\n\n## How to use\n\nThis module just exposes the service layer that will be used to parse your middleware connection to your database.  \n\n```python\nfrom fastapi import FastAPI\nfrom fastapi_sqlalchemy import DBSessionMiddleware\nfrom fastapi_healthcheck import HealthCheckFactory, healthCheckRoute\nfrom fastapi_healthcheck_sqlalchemy import HealthCheckSQLAlchemy\n\n\napp = FastAPI()\n\n# Bring SQLAlchemy online first.\napp.add_middleware(DBSessionMiddleware, db_url=cs.value)\n\n_healthChecks = HealthCheckFactory()\n_healthChecks.add(\n    HealthCheckSQLAlchemy(\n        # The name of the object for your reference\n        alias='postgres db',  \n\n        # The Table that we will run a count method against.\n        table=SmtpContactsSqlModel, \n\n        tags=('postgres', 'db', 'sql01')\n    )\n)\n\napp.add_api_route('/health', endpoint=healthCheckRoute(factory=_healthChecks))\n```\n",
    'author': 'James Tombleson',
    'author_email': 'luther38@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/jtom38/fastapi_healthcheck_sqlalchemy',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
