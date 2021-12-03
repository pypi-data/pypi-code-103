# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['authutils',
 'authutils.oauth2',
 'authutils.oauth2.client',
 'authutils.testing',
 'authutils.testing.fixtures',
 'authutils.token']

package_data = \
{'': ['*']}

install_requires = \
['authlib>=0.11,<1.0',
 'cached-property>=1.4,<2.0',
 'cdiserrors<2.0.0',
 'httpx>=0.12.1,<1.0.0',
 'pyjwt[crypto]>=1.5,<2.0',
 'xmltodict>=0.9,<1.0']

extras_require = \
{'fastapi': ['fastapi>=0.54.1,<0.55.0'], 'flask': ['Flask>=0.10.1']}

setup_kwargs = {
    'name': 'authutils',
    'version': '6.1.1',
    'description': 'Gen3 auth utility functions',
    'long_description': None,
    'author': 'CTDS UChicago',
    'author_email': 'cdis@uchicago.edu',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
