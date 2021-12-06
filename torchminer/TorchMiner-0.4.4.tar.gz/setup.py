# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['torchminer',
 'torchminer.plugins',
 'torchminer.plugins.Logger',
 'torchminer.plugins.Metrics',
 'torchminer.plugins.Recorder']

package_data = \
{'': ['*']}

install_requires = \
['Pillow>=8.4.0,<9.0.0',
 'google-api-python-client>=2.31.0,<3.0.0',
 'ipython>=7.18.0,<8.0.0',
 'matplotlib>=3.5.0,<4.0.0',
 'pandas>=1.3.4,<2.0.0',
 'pylint>=2.12.1,<3.0.0',
 'seaborn>=0.11.2,<0.12.0',
 'sklearn>=0.0,<0.1',
 'tensorboardX>=2.4.1,<3.0.0',
 'torch>=1.8.0,<2.0.0',
 'tqdm>=4.50.0,<5.0.0']

setup_kwargs = {
    'name': 'torchminer',
    'version': '0.4.4',
    'description': 'Run Torch With A Simple Miner',
    'long_description': 'This Project is Forked From [MineTorch](https://github.com/louis-she/minetorch).\n\nPublished on [pypi](https://pypi.org/project/torchminer/)\n\nPackaged Using [Poetry](https://python-poetry.org/)\n\n# Description\nTorchMiner is designed to automatic process the training ,evaluating and testing process for PyTorch DeepLearning,with a simple API.\n\nYou can access all Functions of MineTorch simply use `Miner`.\n',
    'author': 'InEase',
    'author_email': 'inease28@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7.1,<4.0',
}


setup(**setup_kwargs)
