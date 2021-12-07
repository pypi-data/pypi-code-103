# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['dataUtils']

package_data = \
{'': ['*']}

install_requires = \
['fhir.resources>=6.1.0,<7.0.0',
 'insight-engine-schema-python<1.0.0',
 'requests>=2.26,<3.0']

setup_kwargs = {
    'name': 'rialtic-data-dev-py',
    'version': '1.1.14',
    'description': 'Data SDK for development purposes at Rialtic.',
    'long_description': '# Rialtic-Data DEV SDK (Python)\n\nThis repo contains an implementation of the `rialtic-data` interface as first implemented in\nthe `open-insight-marketplace/rialtic-data-python` repository.\n\nAs a development implementation, the content of this repository differs from the one mentioned above in two main ways:\n\n1. The code in this repository is not capable of communicating with the production environment\n2. This repository will contain implementations that allow for easy testing in development, with features such as\n   loading data from a local file or database\n\nAny other differences (such as the testing framework used) are in the effort of bringing this repository more in line\nwith our other Python repos under the `rialtic-community` org, and with our emerging practices and standards in this\norg.\n\nMost crucially, it is important that the interface maintains consistency with whichever implementation is currently used\nby the platform team in production.\n\n# Usage\n\nIn order to connect to the development data servers, an API key is needed. The tests currently expect environment\nvariable called `APIKEY` containing the key. See `test_rialtic_data.py` for an example of how to load and use this key.\n\n',
    'author': 'Rialtic',
    'author_email': 'engines.data@rialtic.io',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://rialtic.io',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
