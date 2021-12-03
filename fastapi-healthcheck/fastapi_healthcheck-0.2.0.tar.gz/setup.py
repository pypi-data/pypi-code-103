# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['fastapi_healthcheck']

package_data = \
{'': ['*']}

install_requires = \
['fastapi>=0.70.0,<0.71.0']

setup_kwargs = {
    'name': 'fastapi-healthcheck',
    'version': '0.2.0',
    'description': 'Base package to handle health checks with FastAPI.',
    'long_description': '# fastapi_healthcheck\n\nEasy to use health check for your FastAPI.  This is the root module that will let you add implement and expand your usage of health checks, with FastAPI.\n\nThis module does not contain any service checkers, but you can easily add them.  The other modules are not in this root module due to different dependencies required for each one.  This is made so you only bring in the packages that you need to not add extra packages.\n\n## Adding Health Checks\n\nHere is what you need to get started.\n\n```python\nfrom fastapi import FastAPI\nfrom fastapi_healthcheck import HealthCheckFactory, healthCheckRoute\n\napp = FastAPI()\n\n# Add Health Checks\n_healthChecks = HealthCheckFactory()\n\n# SQLAlchemy comes from fastapi-healthcheck-sqlalchemy\n_healthChecks.add(HealthCheckSQLAlchemy(alias=\'postgres db\', connectionUri=cs.value, table=SmtpContactsSqlModel, tags=(\'postgres\', \'db\', \'sql01\')))\n\n# This will check external URI and validate the response that is returned.\n# fastapi-healthcheck-uri\n_healthChecks.add(HealthCheckUri(alias=\'reddit\', connectionUri="https://www.reddit.com/r/aww.json", tags=(\'external\', \'reddit\', \'aww\')))\napp.add_api_route(\'/health\', endpoint=healthCheckRoute(factory=_healthChecks))\n\n```\n\n## Returned Data\n\nWhen you request your health check, it will go and check all the entries that have been submitted and run a basic query against them.  If they come back as expected, then a status code is 200.  But if it runs into an error, it will return a 500 error.\n\n```json\n\n{\n    "status":"Healthy",\n    "totalTimeTaken":"0:00:00.671642",\n    "entities":[\n        {\n            "alias":"postgres db",\n            "status":"Healthy",\n            "timeTaken":"0:00:00.009619",\n            "tags":["postgres","db","sql01"]\n        },\n        {\n            "alias":"reddit",\n            "status":"Unhealthy",\n            "timeTaken":"0:00:00.661716",\n            "tags":["external","reddit","aww"]\n        }\n    ]\n}\n```\n\n## Available Modules\n\n* [fastapi_healthcheck_sqlalchemy](https://github.com/jtom38/fastapi_healthcheck_sqlalchemy)\n* [fastapi_healthcheck_uri](https://github.com/jtom38/fastapi_healthcheck_uri)\n\n## Writing a custom module\n\nYou can easily expand on this core module to add other health checks for other services.  Generate a new service that pulls in [HealthCheckInterface]() and [HealthCheckBase]().  With those, you can build the respective class around the interface.\n\nOnce you have your service ready to go, add it to the HealthCheckFactory, and let the testing start.\n',
    'author': 'James Tombleson',
    'author_email': 'luther38@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/jtom38/fastapi_healthcheck',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
