# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['beetsplug']

package_data = \
{'': ['*']}

install_requires = \
['beets>=1.6.0,<2.0.0',
 'mutagen>=1.45.1,<2.0.0',
 'pyfuse3>=3.2.1,<4.0.0',
 'trio>=0.19.0,<0.20.0']

setup_kwargs = {
    'name': 'beets-beetfs',
    'version': '0.8.0',
    'description': 'A beets plugin for mounting a FUSE filesystem of audio items',
    'long_description': None,
    'author': 'Drew Abbott',
    'author_email': 'abbotta4@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
