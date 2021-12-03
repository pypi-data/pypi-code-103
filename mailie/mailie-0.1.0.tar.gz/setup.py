# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['mailie', 'mailie.commands']

package_data = \
{'': ['*']}

install_requires = \
['aiosmtplib>=1.1.6,<2.0.0', 'colorama>=0.4.4,<0.5.0', 'typer>=0.4.0,<0.5.0']

entry_points = \
{'console_scripts': ['mailie = mailie.mailie:app']}

setup_kwargs = {
    'name': 'mailie',
    'version': '0.1.0',
    'description': 'A Python email DSL and CLI with asynchronous sending capabilities.',
    'long_description': '# mailie\nPython DSL and CLI for email.\n',
    'author': 'symonk',
    'author_email': 'jackofspaces@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
