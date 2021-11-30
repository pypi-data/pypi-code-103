# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['nano_chem', 'nano_chem.network', 'nano_chem.utils']

package_data = \
{'': ['*']}

install_requires = \
['ace>=0.3.2,<0.4.0',
 'matplotlib>=3.3.0,<4.0.0',
 'numpy>=1.19.0,<2.0.0',
 'pandas>=1.0.5,<2.0.0',
 'tensorflow>=2.2.0,<3.0.0',
 'torch>=1.5.1,<2.0.0']

setup_kwargs = {
    'name': 'nano-chem',
    'version': '0.1.0',
    'description': 'A Deep Learning Library for Chemistry.',
    'long_description': None,
    'author': 'Xiaomin Wu',
    'author_email': 'xmwu@mail.ustc.edu.cn',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
