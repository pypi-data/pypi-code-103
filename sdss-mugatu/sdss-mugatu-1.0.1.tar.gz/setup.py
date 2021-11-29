# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'python'}

packages = \
['mugatu']

package_data = \
{'': ['*'], 'mugatu': ['etc/*']}

install_requires = \
['fitsio>=1.0.5,<2.0.0',
 'jupyter>=1.0.0,<2.0.0',
 'numpy>=1.19.5,<2.0.0',
 'ortools==9.1.9490',
 'scipy>=1.6.0,<2.0.0',
 'sdss-access>=1.1.1,<2.0.0',
 'sdss-coordio==1.0.0',
 'sdssdb>=0.4.12,<0.5.0']

setup_kwargs = {
    'name': 'sdss-mugatu',
    'version': '1.0.1',
    'description': 'Package to read, write and validate FPS designs',
    'long_description': '# mugatu\n\n![Versions](https://img.shields.io/badge/python->3.7-blue)\n[![Documentation Status](https://readthedocs.org/projects/sdss-mugatu/badge/?version=latest)](https://sdss-mugatu.readthedocs.io/en/latest/?badge=latest)\n[![Travis (.org)](https://img.shields.io/travis/sdss/mugatu)](https://travis-ci.org/sdss/mugatu)\n[![codecov](https://codecov.io/gh/sdss/mugatu/branch/main/graph/badge.svg)](https://codecov.io/gh/sdss/mugatu)\n\nPackage to read, write and validate FPS designs\n',
    'author': 'Ilija Medan',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://pypi.org/project/sdss-mugatu/',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7.1,<4.0.0',
}


setup(**setup_kwargs)
