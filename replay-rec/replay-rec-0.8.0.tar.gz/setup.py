# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['replay',
 'replay.metrics',
 'replay.models',
 'replay.scenarios',
 'replay.scenarios.two_stages',
 'replay.splitters']

package_data = \
{'': ['*']}

install_requires = \
['implicit',
 'lightautoml>=0.3.1',
 'lightfm',
 'llvmlite>=0.32.1',
 'numba>=0.50',
 'numpy>=1.20.0',
 'optuna',
 'pandas',
 'psutil',
 'pyarrow',
 'pyspark>=3.0.0,<4.0.0',
 'pytorch-ignite',
 'scikit-learn',
 'scipy',
 'seaborn',
 'torch']

setup_kwargs = {
    'name': 'replay-rec',
    'version': '0.8.0',
    'description': 'RecSys Library',
    'long_description': '# RePlay\n\nRePlay is a library providing tools for all stages of creating a recommendation system, from data preprocessing to model evaluation and comparison.\n\nRePlay uses PySpark to handle big data.\n\nYou can\n\n- Filter and split data\n- Train models\n- Optimize hyper parameters\n- Evaluate predictions with metrics\n- Combine predictions from different models\n- Create a two-level model\n\n\n## Docs\n\n[Documentation](https://sberbank-ai-lab.github.io/RePlay/)\n\n\n### Installation\n\nUse Linux machine with Python 3.7+ and Java 8+. \n\n```bash\npip install replay-rec\n```\n\nIt is preferable to use a virtual environment for your installation.\n',
    'author': 'AI Lab, Sber',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://sberbank-ai-lab.github.io/RePlay/',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<3.10',
}


setup(**setup_kwargs)
