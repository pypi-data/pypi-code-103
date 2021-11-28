# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['hexagonal',
 'hexagonal.domain',
 'hexagonal.infrastructure',
 'hexagonal.services',
 'hexagonal.use_cases']

package_data = \
{'': ['*']}

install_requires = \
['click>=8.0.3,<9.0.0', 'diagrams>=0.20.0,<0.21.0']

entry_points = \
{'console_scripts': ['hexagonal = hexagonal.infrastructure.cli:main']}

setup_kwargs = {
    'name': 'hexagonal-sanity-check',
    'version': '0.0.15',
    'description': 'Hexagonal Sanity Check',
    'long_description': "# Hexagonal Sanity Check\n\nThis project checks if the dependency flow between the layers of the Hexagonal architecture defined \nfor this project was respected.\n\n### How to configure\n\nFirst it's necessary to define your hexagonal layers and their order.\nThe tool expects a default file name on your source folder dir with the name `hexagonal_config.py`.\n\n1. First you create the Hexagonal Layers you have on your system via the class name HexagonalLayer.\nThere are two arguments: \n   - `name`: It can be any name, `domain`, `frontend`, `infrastructure`, or any name you used for your layers.\n   - `usecases`: This is the name of the directory the files related to this layer as storage. It's not the full path, \njust the directory name.\n\n2. Import `hexagonal_config` on your file, and define the order with `+` (add layers)\nthen `>>`(set the sequence of the layers). The most to the left layers is the most outer layer, while\nthe most to the right layer is the most inner layer.\n\nExample, for this folder structure:\n```\n. src\n├── __init__.py\n├── hexagonal_config.py\n├── domain\n│\xa0\xa0 ├── __init__.py\n│\xa0\xa0 ├── __pycache__\n│\xa0\xa0 └── person.py\n├── infrastructure\n│\xa0\xa0 ├── __init__.py\n│\xa0\xa0 └── person_mysql_repository.py\n├── main.py\n├── services\n│\xa0\xa0 ├── __init__.py\n│\xa0\xa0 └── person_repository.py\n└── usecases\n    ├── __init__.py\n    └── create_person_usecase.py\n```\nThe file:\n```python\nfrom hexagonal.domain.hexagonal_layer import HexagonalLayer\nfrom hexagonal.main import hexagonal_config\n\ninfrastructure_layer = HexagonalLayer(name='infrastructure', directories=['infrastructure'])\nuse_cases_layer = HexagonalLayer(name='use_cases', directories=['usecases'])\nservices_layer = HexagonalLayer(name='services', directories=['services'])\ndomain_layer = HexagonalLayer(name='domain', directories=['domain'])\n\nhexagonal_config + infrastructure_layer >> use_cases_layer >> services_layer >> domain_layer\n```\n\n\n### Generating the Project Diagram\nThis command generate a visual diagram show the composition of your hexagonal layers.\n\n#### Pre requisites\nTo generate the Hexagonal Diagram of the project, it's necessary to have Graphviz installed in the machine.  \nFor Mac you can ``brew install graphviz``.  \nFor other, check the documentation https://graphviz.org/download/. \n\n#### CMD\n`hexagonal diagram --source_path ./` \n\n### Checking Project's Hexagonal Integrity \nThis checks if the correct flow of the dependencies -from outer to inner layer- was respected.\n\n#### CMD\n`hexagonal check --source_path ./`\n\n",
    'author': 'rfrezino',
    'author_email': 'rodrigofrezino@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
