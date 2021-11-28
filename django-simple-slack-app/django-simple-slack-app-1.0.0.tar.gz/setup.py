# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['django_simple_slack_app', 'django_simple_slack_app.migrations']

package_data = \
{'': ['*'], 'django_simple_slack_app': ['templates/django_simple_slack_app/*']}

install_requires = \
['django>=3.0.4,<4.0.0',
 'hgtk>=0.1.3,<0.2.0',
 'pyee>=7.0.1,<8.0.0',
 'slackclient>=2.5.0,<3.0.0',
 'slackeventsapi>=2.1.0,<3.0.0']

setup_kwargs = {
    'name': 'django-simple-slack-app',
    'version': '1.0.0',
    'description': 'nice toolkit for Slack app(bot) that support Event API & OAuth',
    'long_description': None,
    'author': 'Matthew, Lee',
    'author_email': 'bluedisk@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
