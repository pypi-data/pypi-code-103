# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pydantic_schemaorg']

package_data = \
{'': ['*']}

install_requires = \
['pydantic>=1.8.2,<2.0.0']

setup_kwargs = {
    'name': 'pydantic-schemaorg',
    'version': '0.0.2',
    'description': 'Pydantic classes for Schema.org',
    'long_description': '# pydantic_schemaorg\n',
    'author': 'Reinoud Baker',
    'author_email': 'reinoud@lexiq.nl',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/lexiq-legal/pydantic_schemaorg',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
}


setup(**setup_kwargs)
