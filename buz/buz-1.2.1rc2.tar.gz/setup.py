# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['buz',
 'buz.command',
 'buz.command.middleware',
 'buz.command.sync',
 'buz.event',
 'buz.event.kombu',
 'buz.event.kombu.consume_strategy',
 'buz.event.kombu.execution_strategy',
 'buz.event.kombu.publish_strategy',
 'buz.event.kombu.retry',
 'buz.event.middleware',
 'buz.event.sync',
 'buz.locator',
 'buz.locator.pypendency',
 'buz.locator.sync',
 'buz.middleware',
 'buz.query',
 'buz.query.middleware',
 'buz.query.sync']

package_data = \
{'': ['*']}

extras_require = \
{':python_full_version < "3.7.0"': ['dataclasses>=0.8,<0.9'],
 'kombu': ['kombu>=4.6.11'],
 'pypendency': ['pypendency>=0.1.0,<0.2.0']}

setup_kwargs = {
    'name': 'buz',
    'version': '1.2.1rc2',
    'description': 'Buz is a set of light, simple and extensible implementations of event, command and query buses.',
    'long_description': '# Buz\n\nBuz is a set of light, simple and extensible implementations of event, command and query buses.\n ',
    'author': 'Luis Pintado Lozano',
    'author_email': 'luis.pintado.lozano@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'extras_require': extras_require,
    'python_requires': '>=3.6.9,<4.0.0',
}


setup(**setup_kwargs)
