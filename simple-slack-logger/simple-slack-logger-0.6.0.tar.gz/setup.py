# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['slack_logger']

package_data = \
{'': ['*']}

install_requires = \
['requests>=2.23.0,<3.0.0']

setup_kwargs = {
    'name': 'simple-slack-logger',
    'version': '0.6.0',
    'description': 'Logging handler to send messages to a Slack channel.',
    'long_description': '[![PyPi](https://img.shields.io/pypi/v/simple-slack-logger)](https://pypi.org/project/simple-slack-logger/)\n[![Code style](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)\n[![License](https://img.shields.io/pypi/l/simple-slack-logger)](http://www.apache.org/licenses/LICENSE-2.0)\n[![Versions](https://img.shields.io/pypi/pyversions/simple-slack-logger)](https://pypi.org/project/simple-slack-logger/)\n[![CodeFactor](https://www.codefactor.io/repository/github/gixproject/simple-slack-logger/badge)](https://www.codefactor.io/repository/github/gixproject/simple-slack-logger)\n\n# Simple logging with Slack\n\nIt helps you to receive all logs from your Python code in Slack channels\nusing [webhooks](https://api.slack.com/messaging/webhooks).\n\nInstall from PyPi:  \n`pip install simple-slack-logger`\n\nor from repository:  \n`pip install git+https://github.com/gixproject/simple-slack-logger `\n\n## Usage\n\n### Explicit usage\n\n```python\nimport logging\nfrom slack_logger import SlackHandler\n\nlogger = logging.getLogger(__name__)\nhandler = SlackHandler(webhook="<YOUR_WEBHOOK>")\nlogger.addHandler(handler)\nlogger.error("Something bad happened")\n```\n\n### Logging config\n\n```python\n"handlers": {\n    "slack": {\n        "class": "slack_logger.SlackHandler",\n        "formatter": "default",\n        "level": "WARNING",\n        "webhook": "<YOUR_WEBHOOK>",\n    },\n}\n```\n\n### Hint\n\nTo catch all exceptions from your Python code you can use this in the main module:\n\n```python\ndef logging_except_hook(exc_type, exc_value, exc_traceback):\n    logging.error("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))\n\n\nsys.excepthook = logging_except_hook\n```',
    'author': 'giX',
    'author_email': 'viacheslavlab@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/gixproject/simple-slack-logger',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
