# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pydiar', 'pydiar.models', 'pydiar.models.binary_key', 'pydiar.util']

package_data = \
{'': ['*']}

install_requires = \
['numpy>=1.21.4,<2.0.0',
 'python_speech_features>=0.6,<0.7',
 'scikit-learn>=1.0.1,<2.0.0',
 'scipy>=1.7.3,<2.0.0',
 'webrtcvad>=2.0.10,<3.0.0']

setup_kwargs = {
    'name': 'pydiar',
    'version': '0.0.1',
    'description': '',
    'long_description': None,
    'author': 'pajowu',
    'author_email': 'git@ca.pajowu.de',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<3.11',
}


setup(**setup_kwargs)
