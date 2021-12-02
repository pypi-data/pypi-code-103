# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['snatch', 'snatch.base', 'snatch.helpers']

package_data = \
{'': ['*']}

install_requires = \
['arrow',
 'asbool',
 'boto3',
 'loguru',
 'marshmallow',
 'marshmallow_enum',
 'python-dotenv',
 'requests',
 'scalpl',
 'validate-docbr']

extras_require = \
{':python_version >= "3.7" and python_version < "4.0"': ['typing_extensions']}

setup_kwargs = {
    'name': 'py-snatch',
    'version': '2.17.2',
    'description': "The Friendly Integration Library for Data Scientists. Don't You Just Know It?",
    'long_description': None,
    'author': 'A55 Tech',
    'author_email': 'tech@a55.tech',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
