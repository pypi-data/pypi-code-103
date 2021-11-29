# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['df', 'df.scripts']

package_data = \
{'': ['*']}

install_requires = \
['DeepFilterLib>=0.1.6,<0.2', 'loguru>=0.5', 'numpy>=1.20,<2.0']

extras_require = \
{'train': ['DeepFilterDataLoader>=0.1.6,<0.2', 'icecream>=2,<3']}

entry_points = \
{'console_scripts': ['deepFilter = df.enhance:main']}

setup_kwargs = {
    'name': 'deepfilternet',
    'version': '0.1.8',
    'description': 'Noise supression using deep filtering',
    'long_description': None,
    'author': 'Hendrik Schröter',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/Rikorose/DeepFilterNet',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
