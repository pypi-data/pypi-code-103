# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['avantpy', 'avantpy.dialects', 'avantpy.wrappers']

package_data = \
{'': ['*'],
 'avantpy': ['locales/*',
             'locales/fr/LC_MESSAGES/*',
             'locales/ga/LC_MESSAGES/*']}

install_requires = \
['PyYAML>=6.0,<7.0',
 'Unidecode>=1.3.2,<2.0.0',
 'friendly-traceback==0.0.10',
 'requests>=2.26.0,<3.0.0',
 'unicode>=2.8,<3.0',
 'xdg>=5.1.1,<6.0.0']

setup_kwargs = {
    'name': 'avantpy-extended',
    'version': '0.1.2',
    'description': 'AvantPy with Extensions',
    'long_description': None,
    'author': 'André Roberge',
    'author_email': 'andre.roberge@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
