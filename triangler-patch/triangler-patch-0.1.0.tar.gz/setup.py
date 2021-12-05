# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['triangler']

package_data = \
{'': ['*']}

install_requires = \
['numba>=0.54.1,<0.55.0', 'scikit-image>=0.19.0,<0.20.0']

setup_kwargs = {
    'name': 'triangler-patch',
    'version': '0.1.0',
    'description': '',
    'long_description': None,
    'author': 'djkcyl',
    'author_email': 'cyl@cyllive.cn',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<3.10',
}


setup(**setup_kwargs)
