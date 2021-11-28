# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['desdeo_problem',
 'desdeo_problem.problem',
 'desdeo_problem.surrogatemodels',
 'desdeo_problem.testproblems']

package_data = \
{'': ['*']}

install_requires = \
['diversipy>=0.8.0,<0.9.0',
 'numpy>=1.17,<2.0',
 'optproblems>=1.2,<2.0',
 'pandas>=1.0,<2.0',
 'scikit-learn>=0.24.0']

setup_kwargs = {
    'name': 'desdeo-problem',
    'version': '1.3.3',
    'description': 'This package contains the problem classes for desdeo framework.',
    'long_description': None,
    'author': 'Bhupinder Saini',
    'author_email': 'bhupinder.s.saini@jyu.fi',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<3.10',
}


setup(**setup_kwargs)
