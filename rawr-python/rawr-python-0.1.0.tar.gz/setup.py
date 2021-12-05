# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['rawr_python', 'rawr_python.classes', 'rawr_python.resources']

package_data = \
{'': ['*']}

install_requires = \
['boltons>=21.0.0,<22.0.0', 'pydantic>=1.8.2,<2.0.0']

setup_kwargs = {
    'name': 'rawr-python',
    'version': '0.1.0',
    'description': 'Python Riot API Wrapper',
    'long_description': None,
    'author': 'Ben Dowling',
    'author_email': 'ben.dowling@icloud.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
