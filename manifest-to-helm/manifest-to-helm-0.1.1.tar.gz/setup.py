# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['manifest_to_helm']

package_data = \
{'': ['*']}

install_requires = \
['PyYAML>=6.0,<7.0']

setup_kwargs = {
    'name': 'manifest-to-helm',
    'version': '0.1.1',
    'description': 'A helper library to convert Kubernetes YAML manifests to Helm charts',
    'long_description': None,
    'author': 'John Carter',
    'author_email': 'jfcarter2358@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
