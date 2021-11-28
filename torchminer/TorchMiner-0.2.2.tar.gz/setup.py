# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['torchminer',
 'torchminer.plugins',
 'torchminer.plugins.Drawer',
 'torchminer.plugins.Logger',
 'torchminer.plugins.Sheet']

package_data = \
{'': ['*']}

install_requires = \
['google-api-python-client>=2.31.0,<3.0.0',
 'ipython>=7.18.0,<8.0.0',
 'matplotlib>=3.5.0,<4.0.0',
 'pandas>=1.3.4,<2.0.0',
 'seaborn>=0.11.2,<0.12.0',
 'sklearn>=0.0,<0.1',
 'tensorboardX>=2.4.1,<3.0.0',
 'torch>=1.8.0,<2.0.0',
 'tqdm>=4.50.0,<5.0.0']

setup_kwargs = {
    'name': 'torchminer',
    'version': '0.2.2',
    'description': 'Run Torch With A Simple Miner',
    'long_description': "This Project is Forked From [MineTorch](https://github.com/louis-she/minetorch).\n\nPublished on [pypi](https://pypi.org/project/torchminer/)\n\nPackaged Using [Poetry](https://python-poetry.org/)\n\n# Description\nTorchMiner is designed to automatic process the training ,evaluating and testing process for PyTorch DeepLearning,with a simple API.\n\nYou can access all Functions of MineTorch simply use `Miner`.\n\n## Project ToDo\n\n [] Make Console Output a plugin \n \n [] Abstract Plugin Manager\n\n [] Move ***Drawer*** Operations Outside of Miner as a Plugin\n \n [] Add Plugin Able And Disable Stat\n \n [] Move Miner Options to yaml File, Add Config Class\n \n Now Plugins only supports output functions, they can't modify or change the data of the Miner class.Any Ideas? I am glad to know.\n \n [] Write about my design concept",
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
