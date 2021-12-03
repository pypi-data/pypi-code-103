# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pydeal_line_length']

package_data = \
{'': ['*']}

install_requires = \
['pylint>=2.12.1,<3.0.0']

setup_kwargs = {
    'name': 'pydeal-line-length',
    'version': '0.1.0',
    'description': 'A pylint checker to enforce line lengths compatible with ideal monitors',
    'long_description': None,
    'author': 'Zach Banks',
    'author_email': 'zjbanks@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
