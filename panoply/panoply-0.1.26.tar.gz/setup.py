# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['panoply']

package_data = \
{'': ['*']}

install_requires = \
['simple_term_menu>=1.4.1,<2.0.0']

entry_points = \
{'console_scripts': ['panoply = panoply.panoply:main']}

setup_kwargs = {
    'name': 'panoply',
    'version': '0.1.26',
    'description': '',
    'long_description': None,
    'author': 'Jeremy Naccache',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
