# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['glennopt',
 'glennopt.DOE',
 'glennopt.base',
 'glennopt.helpers',
 'glennopt.io',
 'glennopt.optimizers']

package_data = \
{'': ['*']}

install_requires = \
['dataclasses_json',
 'diversipy',
 'doepy',
 'matplotlib>=3.3.1,<4.0.0',
 'numpy',
 'pandas',
 'psutil',
 'pydoe',
 'tqdm']

setup_kwargs = {
    'name': 'glennopt',
    'version': '1.3.1',
    'description': 'Multi and single objective optimization tool for cfd/computer simulations.',
    'long_description': None,
    'author': 'Paht Juangphanich',
    'author_email': 'paht.juangphanich@nasa.gov',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6.9,<4.0.0',
}


setup(**setup_kwargs)
