# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['image_preprocessing']

package_data = \
{'': ['*']}

install_requires = \
['Pillow>=8.4.0,<9.0.0',
 'dlib>=19.22.1,<20.0.0',
 'imutils>=0.5.4,<0.6.0',
 'numpy>=1.21.4,<2.0.0',
 'opencv-python>=4.5.4,<5.0.0',
 'tqdm>=4.62.3,<5.0.0']

setup_kwargs = {
    'name': 'dg-util',
    'version': '0.0.13',
    'description': 'commom tools',
    'long_description': None,
    'author': 'DataGrid',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<3.11',
}


setup(**setup_kwargs)
