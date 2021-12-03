# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['fastapi_healthcheck_uri']

package_data = \
{'': ['*']}

install_requires = \
['fastapi-healthcheck>=0.2.2,<0.3.0', 'requests>=2.26.0,<3.0.0']

setup_kwargs = {
    'name': 'fastapi-healthcheck-uri',
    'version': '0.1.0',
    'description': 'A module to have a FastAPI HealthCheck reach out to a URI to validate external service health.',
    'long_description': '# fastapi_healthcheck_uri\n\nA module to have a FastAPI HealthCheck reach out to a URI to validate external service health.\n\n## Adding Health Checks\n\nHere is what you need to get started.\n\n```python\nfrom fastapi import FastAPI\nfrom fastapi_healthcheck import HealthCheckFactory, healthCheckRoute\nfrom fastapi_healthcheck_uri import HealthCheckUri\n\napp = FastAPI()\n\n# Add Health Checks\n_healthChecks = HealthCheckFactory()\n_healthChecks.add(\n    HealthCheckUri(\n        alias=\'reddit\', \n        connectionUri="https://www.reddit.com/r/aww.json", \n        tags=(\'external\', \'reddit\', \'aww\'),\n        healthyCode=200,\n        unhealthyCode=500\n    )\n)\napp.add_api_route(\'/health\', endpoint=healthCheckRoute(factory=_healthChecks))\n\n```\n',
    'author': 'James Tombleson',
    'author_email': 'luther38@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/jtom38/fastapi_healthcheck_uri',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
