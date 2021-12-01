# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['media_hoard_cli', 'tests']

package_data = \
{'': ['*']}

install_requires = \
['click']

entry_points = \
{'console_scripts': ['media_hoard_cli = media_hoard_cli.cli:main']}

setup_kwargs = {
    'name': 'media-hoard-cli',
    'version': '0.1.0',
    'description': 'Top-level package for Media Hoard CLI.',
    'long_description': '\nMedia Hoard CLI\n\n* Free software: MIT License\n\nFeatures\n--------\n\n* TODO\n\n\nCredits\n-------\n\nThis package was created with Cookiecutter_ and the `midwatch/cc-py3-pkg`_ project template.\n\n.. _Cookiecutter: https://github.com/audreyr/cookiecutter\n.. _`midwatch/cc-py3-pkg`: https://github.com/midwatch/cc-py3-pkg\n',
    'author': 'Justin Stout',
    'author_email': 'midwatch@jstout.us',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/midwatch/media_hoard_cli',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
