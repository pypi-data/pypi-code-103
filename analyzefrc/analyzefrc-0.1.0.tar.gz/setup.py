# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['analyzefrc']

package_data = \
{'': ['*']}

install_requires = \
['Pillow>=8.3.2,<9.0.0',
 'deco>=0.6.3,<0.7.0',
 'frc>=0.1.0,<0.2.0',
 'loess>=2.1.1,<3.0.0',
 'matplotlib>=3.4,<4.0',
 'readlif>=0.6.5,<0.7.0']

setup_kwargs = {
    'name': 'analyzefrc',
    'version': '0.1.0',
    'description': 'Plots, analysis and resolution measurement of microscopy images using Fourier Ring Correlation (FRC).',
    'long_description': None,
    'author': 'Tip ten Brink',
    'author_email': 'T.M.tenBrink@student.tudelft.nl',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<3.10',
}


setup(**setup_kwargs)
