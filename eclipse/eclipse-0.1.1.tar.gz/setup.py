# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['eclipse']

package_data = \
{'': ['*']}

install_requires = \
['ftfy>=6.0.3,<7.0.0',
 'regex>=2021.11.10,<2022.0.0',
 'torch>=1.7.1,<2.0.0',
 'torchvision>=0.11.1,<0.12.0',
 'tqdm>=4.62.3,<5.0.0']

setup_kwargs = {
    'name': 'eclipse',
    'version': '0.1.1',
    'description': "A simplified and extended version of OpenAI's Contrastive Language-Image Pretraining",
    'long_description': None,
    'author': 'CWDT',
    'author_email': 'null@cwdt.us',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
