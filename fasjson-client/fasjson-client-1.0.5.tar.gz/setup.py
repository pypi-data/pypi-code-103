# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['fasjson_client',
 'fasjson_client.cli',
 'fasjson_client.tests',
 'fasjson_client.tests.unit']

package_data = \
{'': ['*'], 'fasjson_client.tests.unit': ['fixtures/*']}

install_requires = \
['bravado>=10.6.0,<12',
 'gssapi>=1.5.1,<2.0.0',
 'requests-gssapi>=1.2.1,<2.0.0',
 'requests>=2.20.0,<3.0.0',
 'toml>=0.10.0,<0.11.0']

extras_require = \
{'cli': ['cryptography>=2.3', 'click>=6.7,<9']}

entry_points = \
{'console_scripts': ['fasjson-client = fasjson_client.cli:cli']}

setup_kwargs = {
    'name': 'fasjson-client',
    'version': '1.0.5',
    'description': 'An OpenAPI client for FASJSON',
    'long_description': '# fasjson-client\n\nA python client library for the FASJSON API\n\nThis client uses the bravado library to build dynamic api methods based on open-api specs (version 2.0): https://github.com/Yelp/bravado\n\nThe documentation is available at https://fasjson-client.readthedocs.io/\n\n## License\n\nLicensed under [lgpl-3.0](./LICENSE)\n',
    'author': 'Fedora Infrastructure',
    'author_email': 'infrastructure@lists.fedoraproject.org',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/fedora-infra/fasjson-client',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
