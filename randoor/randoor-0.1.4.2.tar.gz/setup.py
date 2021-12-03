# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['randoor', 'randoor.generator', 'randoor.spawner']

package_data = \
{'': ['*']}

install_requires = \
['Shapely>=1.7.0,<2.0.0', 'cython>=0.29.24,<0.30.0', 'trimesh>=3.9.34,<4.0.0']

extras_require = \
{':python_version >= "2.7" and python_version < "3.0"': ['scikit-learn==0.20',
                                                         'numpy-quaternion==2019.12.11.22.25.52',
                                                         'pyglet==1.5.0'],
 ':python_version >= "3.7"': ['scikit-learn>=1.0.1,<2.0.0',
                              'numpy-quaternion==2021.10.7.23.40.37',
                              'pyglet>=1.5.21,<2.0.0']}

setup_kwargs = {
    'name': 'randoor',
    'version': '0.1.4.2',
    'description': 'Generate randomized indoor scene.',
    'long_description': None,
    'author': 'Reona Sato',
    'author_email': 'www.shinderu.www@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/wwwshwww/randoor',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*, !=3.4.*, !=3.5.*, !=3.6.*',
}


setup(**setup_kwargs)
