# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['grams', 'grams.algorithm', 'grams.inputs']

package_data = \
{'': ['*']}

install_requires = \
['beautifulsoup4>=4.9.3,<5.0.0',
 'click>=8.0.1,<9.0.0',
 'elasticsearch>=7.12.1,<8.0.0',
 'fastnumbers>=3.1.0,<4.0.0',
 'ftfy>=6.0.1,<7.0.0',
 'fuzzywuzzy>=0.18.0,<0.19.0',
 'html5lib>=1.1,<2.0',
 'ipython>=7.22.0,<8.0.0',
 'kgdata>=1.3.0,<2.0.0',
 'loguru>=0.5.3,<0.6.0',
 'matplotlib>=3.4.1,<4.0.0',
 'ned>=1.0.0,<2.0.0',
 'networkx>=2.5.1,<3.0.0',
 'omegaconf>=2.0.6,<3.0.0',
 'orjson>=3.5.2,<4.0.0',
 'pslpython>=2.2.2,<3.0.0',
 'pydot>=1.4.2,<2.0.0',
 'python-Levenshtein>=0.12.2,<0.13.0',
 'python-dotenv>=0.19.0',
 'python-slugify>=5.0.2,<6.0.0',
 'rdflib>=5.0.0,<6.0.0',
 'redis>=3.5.3,<4.0.0',
 'requests>=2.25.1,<3.0.0',
 'rltk==2.0.0-alpha.15',
 'ruamel.yaml>=0.17.4,<0.18.0',
 'sem-desc>=1.2.3,<2.0.0',
 'steiner-tree>=1.0.0,<2.0.0',
 'tqdm>=4.60.0,<5.0.0',
 'typing_extensions>=3.10,<4.0',
 'ujson>=4.0.2,<5.0.0']

entry_points = \
{'console_scripts': ['grams = grams.cli:cli']}

setup_kwargs = {
    'name': 'sm-grams',
    'version': '1.2.4',
    'description': '',
    'long_description': None,
    'author': 'Binh Vu',
    'author_email': 'binh@toan2.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
