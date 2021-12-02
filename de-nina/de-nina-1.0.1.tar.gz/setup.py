# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['deutschland',
 'deutschland.nina',
 'deutschland.nina.api',
 'deutschland.nina.apis',
 'deutschland.nina.model',
 'deutschland.nina.models']

package_data = \
{'': ['*']}

install_requires = \
['python-dateutil', 'urllib3>=1.25.3']

setup_kwargs = {
    'name': 'de-nina',
    'version': '1.0.1',
    'description': 'Bundesamt für Bevölkerungsschutz: NINA API',
    'long_description': None,
    'author': 'BundesAPI',
    'author_email': 'kontakt@bund.dev',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/bundesAPI/autobahn-api',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6',
}


setup(**setup_kwargs)
