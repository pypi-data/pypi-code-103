# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['snakeboost']

package_data = \
{'': ['*']}

install_requires = \
['attr>=0.3.1,<0.4.0']

setup_kwargs = {
    'name': 'snakeboost',
    'version': '0.1.0',
    'description': 'Utility functions to turbocharge your snakemake workflows. Virtualenvs, tarfiles, and more.',
    'long_description': None,
    'author': 'Peter Van Dyken',
    'author_email': 'pvandyk2@uwo.ca',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<3.11',
}


setup(**setup_kwargs)
