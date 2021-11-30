# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['epymetheus',
 'epymetheus.benchmarks',
 'epymetheus.datasets',
 'epymetheus.metrics',
 'epymetheus.stochastic',
 'epymetheus.strategy',
 'epymetheus.ts']

package_data = \
{'': ['*']}

install_requires = \
['numpy>=1.21.4,<2.0.0',
 'pandas-datareader>=0.10.0,<0.11.0',
 'pandas>=1.3.4,<2.0.0']

setup_kwargs = {
    'name': 'epymetheus',
    'version': '0.17.0',
    'description': 'Multi-asset Backtesting Framework',
    'long_description': None,
    'author': 'Shota Imaki',
    'author_email': 'shota.imaki.0801@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/epymetheus/epymetheus',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7.12,<3.11',
}


setup(**setup_kwargs)
