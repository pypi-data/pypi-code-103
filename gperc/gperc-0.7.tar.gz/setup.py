# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['gperc', 'gperc.fastlibs']

package_data = \
{'': ['*'], 'gperc.fastlibs': ['src/*']}

install_requires = \
['datasets==1.12.1',
 'fire>=0.4.0,<0.5.0',
 'numpy>=1.19.0,<2.0.0',
 'torch>=1.9.0,<2.0.0',
 'tqdm>=4.62.2,<5.0.0']

setup_kwargs = {
    'name': 'gperc',
    'version': '0.7',
    'description': 'General purpose perceiver architectures!',
    'long_description': None,
    'author': 'yashbonde',
    'author_email': 'bonde.yash97@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
