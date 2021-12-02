# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

modules = \
['notion_tools']
install_requires = \
['notion-client>=0.4', 'pandas>=1.0']

setup_kwargs = {
    'name': 'notion-tools',
    'version': '0.1.1',
    'description': 'Python and pandas helpers for Notion',
    'long_description': None,
    'author': 'Patch Biosciences, Inc.',
    'author_email': 'contact@patch.bio',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'py_modules': modules,
    'install_requires': install_requires,
    'python_requires': '>=3.6',
}


setup(**setup_kwargs)
