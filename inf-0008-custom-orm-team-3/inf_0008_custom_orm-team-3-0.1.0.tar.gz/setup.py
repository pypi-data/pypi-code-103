# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['inf_0008_custom_orm-team-3']

package_data = \
{'': ['*']}

entry_points = \
{'console_scripts': ['APPLICATION-NAME = entry:main']}

setup_kwargs = {
    'name': 'inf-0008-custom-orm-team-3',
    'version': '0.1.0',
    'description': '',
    'long_description': None,
    'author': 'Belligraf',
    'author_email': 'belligraf@mail.ru',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
