# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['qulacsvis', 'qulacsvis.utils', 'qulacsvis.visualization']

package_data = \
{'': ['*']}

install_requires = \
['Pillow>=8.3.2,<9.0.0',
 'Qulacs>=0.3.0,<0.4.0',
 'matplotlib>=3.4.3,<4.0.0',
 'numpy>=1.21.2,<2.0.0',
 'temp>=2020.7.2,<2021.0.0']

setup_kwargs = {
    'name': 'qulacsvis',
    'version': '0.1.0',
    'description': 'visualizers for qulacs',
    'long_description': '# qulacs-visualizer\nvisualizers for qulacs\n',
    'author': 'Qulacs-Osaka',
    'author_email': 'you@example.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/Qulacs-Osaka/qulacs-visualizer',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<3.11',
}


setup(**setup_kwargs)
