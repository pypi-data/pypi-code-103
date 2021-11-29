# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['tom_iag']

package_data = \
{'': ['*']}

install_requires = \
['requests']

setup_kwargs = {
    'name': 'tom-iag',
    'version': '0.2.2',
    'description': 'IAG telescopes facility module for the TOM Toolkit',
    'long_description': '# TOM oservation facility interface for the IAG telescopes.\n\n## Features\nThis module adds support to the TOM Toolkit for the IAG telescopes (MONET/N, MONET/S IAG50cm).\n\n',
    'author': 'Tim-Oliver Husser',
    'author_email': 'thusser@uni-goettingen.de',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/thusser/tom_iag',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<3.11',
}


setup(**setup_kwargs)
