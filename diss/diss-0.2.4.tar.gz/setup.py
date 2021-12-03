# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['diss', 'diss.domains']

package_data = \
{'': ['*']}

install_requires = \
['attrs>=21.0,<22.0',
 'funcy>=1.16,<2.0',
 'numpy>=1.21.2,<2.0.0',
 'scipy>=1.7.2,<2.0.0']

setup_kwargs = {
    'name': 'diss',
    'version': '0.2.4',
    'description': 'Demonstration Informed Specification Search',
    'long_description': None,
    'author': 'Marcell Vazquez-Chanlatte',
    'author_email': 'mvc@linux.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<3.11',
}


setup(**setup_kwargs)
