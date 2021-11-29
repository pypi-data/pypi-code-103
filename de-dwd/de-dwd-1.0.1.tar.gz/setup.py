# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['deutschland',
 'deutschland.dwd',
 'deutschland.dwd.api',
 'deutschland.dwd.apis',
 'deutschland.dwd.model',
 'deutschland.dwd.models']

package_data = \
{'': ['*']}

install_requires = \
['python-dateutil', 'urllib3>=1.25.3']

setup_kwargs = {
    'name': 'de-dwd',
    'version': '1.0.1',
    'description': 'Deutscher Wetterdienst: API',
    'long_description': None,
    'author': 'BundesAPI',
    'author_email': 'kontakt@bund.dev',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/bundesAPI/dwd-api',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6',
}


setup(**setup_kwargs)
