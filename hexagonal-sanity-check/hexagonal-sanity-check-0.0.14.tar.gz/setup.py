# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['src', 'src.domain', 'src.infrastructure', 'src.services', 'src.use_cases']

package_data = \
{'': ['*']}

install_requires = \
['click>=8.0.3,<9.0.0', 'diagrams>=0.20.0,<0.21.0']

setup_kwargs = {
    'name': 'hexagonal-sanity-check',
    'version': '0.0.14',
    'description': 'Hexagonal Sanity Check',
    'long_description': "# Hexagonal Sanity Check\n\nThis project checks if the dependency flow between the layers of the Hexagonal architecture defined \nfor this project was respected.\n\n### How to configure\n\nFirst it's necessary to define your hexagonal layers and their order.\n\n### Generating the Project Diagram\n\nTo generate the Hexagonal Diagram of the project, it's necessary to have Graphviz installed in the machine.  \nFor Mac you can ``brew install graphviz``.  \nFor other, check the documentation https://graphviz.org/download/. \n\n",
    'author': 'rfrezino',
    'author_email': 'rodrigofrezino@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
