# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['kicksaw_lambda_logger']

package_data = \
{'': ['*']}

install_requires = \
['sentry-sdk>=1.5.0,<2.0.0']

setup_kwargs = {
    'name': 'kicksaw-lambda-logger',
    'version': '0.0.1',
    'description': 'A customized loger for seamlessly logging on an AWS Lambda or local environment, with reporting in Sentry and other logging-related featues',
    'long_description': '# kicksaw-lambda-logger\n\nThis is intended for use with Kicksaw\'s integration projects and our other open-source libraries like\n[pycm](https://github.com/Kicksaw-Consulting/python-configuration-management). However, these aren\'t\nhard dependencies.\n\n# Usage\n\n```python\nfrom kicksaw_lambda_logger import get_logger\n\nlogger = get_logger(__name__)\n\nlogger.info("Logging is fun!")\n```\n\n# Environment variables\n\nThere are two environment variables this library makes use of:\n\n- `STAGE`\n- `LOG_LEVEL`\n\n`STAGE` represents your deployment environment, e.g., `production`, `development`, `local`, or `test`. This affects\nwhich logging mechanism the library uses under the hood.\n\n`LOG_LEVEL` represents the log level, e.g., `DEBUG`, `INFO`, `WARNING`, or `ERROR`.\n\n# Sentry\n\nAs this library grows, we\'ll be adding more helper methods for reporting in Sentry. For now, you can send an exception\nto Sentry without your code dying by using `send_exception_to_sentry`.\n\n# Future plans\n\n- Write all logs to `tmp` so that other reporting tools can sweep the logs and do something with them\n- Add moe Sentry features\n- Pass in stage and level from outside?\n\n---\n\nThis project uses [poetry](https://python-poetry.org/) for dependency management\nand packaging.\n',
    'author': 'Alex Drozd',
    'author_email': 'alex@kicksaw.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/Kicksaw-Consulting/kicksaw-lambda-logger',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
