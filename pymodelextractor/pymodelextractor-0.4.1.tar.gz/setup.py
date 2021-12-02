# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pymodelextractor',
 'pymodelextractor.learners',
 'pymodelextractor.learners.observation_table_learners',
 'pymodelextractor.learners.observation_table_learners.translators',
 'pymodelextractor.learners.observation_tree_learners',
 'pymodelextractor.teachers',
 'pymodelextractor.tests',
 'pymodelextractor.tests.learners_tests',
 'pymodelextractor.utilities']

package_data = \
{'': ['*']}

install_requires = \
['pythautomata==0.11.2']

setup_kwargs = {
    'name': 'pymodelextractor',
    'version': '0.4.1',
    'description': '',
    'long_description': None,
    'author': 'Federico VIlensky',
    'author_email': 'fedevilensky@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
