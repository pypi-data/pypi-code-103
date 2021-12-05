# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['triangler']

package_data = \
{'': ['*']}

install_requires = \
['numba>=0.53.1,<0.54.0', 'numpy==1.21.4', 'scikit-image>=0.19.0,<0.20.0']

setup_kwargs = {
    'name': 'triangler-patch',
    'version': '0.1.2',
    'description': 'triangler dependencies version patch',
    'long_description': None,
    'author': 'djkcyl',
    'author_email': 'cyl@cyllive.cn',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/tdh8316/triangler',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<3.10',
}


setup(**setup_kwargs)
