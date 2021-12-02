# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['deepprojection']

package_data = \
{'': ['*']}

install_requires = \
['albumentations>=0.5.2,<0.6.0',
 'barbar>=0.2.1,<0.3.0',
 'kornia>=0.5,<0.6',
 'numpy>=1.19.5,<2.0.0',
 'tifffile',
 'tqdm>=4.61.2,<5.0.0']

setup_kwargs = {
    'name': 'deepprojection',
    'version': '0.0.9',
    'description': 'Trainable projection of 3D microscopy stacks using deep learning',
    'long_description': None,
    'author': 'Daniel Haertter',
    'author_email': 'dani.hae@posteo.de',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
