# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pysentimiento', 'pysentimiento.baselines']

package_data = \
{'': ['*']}

install_requires = \
['datasets>=1.13.3,<2.0.0',
 'emoji>=1.6.1,<2.0.0',
 'sklearn>=0.0,<0.1',
 'torch>=1.9.0,<2.0.0',
 'transformers>=4.11.3,<5.0.0']

setup_kwargs = {
    'name': 'pysentimiento',
    'version': '0.3.2',
    'description': 'A Transformer-based library for SocialNLP tasks',
    'long_description': None,
    'author': 'Juan Manuel Pérez',
    'author_email': 'jmperez@dc.uba.ar',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<3.10',
}


setup(**setup_kwargs)
