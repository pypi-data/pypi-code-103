# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['hpc_helper']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'hpc-helper',
    'version': '0.1.3',
    'description': "Python package with helper functions for working with FAU's High Performance Cluster (HPC).",
    'long_description': "# hpc-helper\n\n[![PyPI](https://img.shields.io/pypi/v/hpc-helper)](https://pypi.org/project/hpc-helper/)\n![GitHub](https://img.shields.io/github/license/mad-lab-fau/hpc-helper)\n[![Test and Lint](https://github.com/mad-lab-fau/hpc-helper/actions/workflows/test-and-lint.yml/badge.svg)](https://github.com/mad-lab-fau/hpc-helper/actions/workflows/test-and-lint.yml)\n[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)\n![PyPI - Downloads](https://img.shields.io/pypi/dm/hpc-helper)\n![GitHub commit activity](https://img.shields.io/github/commit-activity/m/mad-lab-fau/hpc-helper)\n\nPython package with helper functions for working with FAU's [High Performance Cluster](https://hpc.fau.de/) (HPC).\n\n## Installation\n\n``hpc-helper`` requires Python >=3.7. First, install a compatible version of Python. \nThen you can install ``hpc-helper`` via pip. \n\nInstallation from [PyPi](https://pypi.org/): \n```bash\npip install hpc_helper\n```\n\nInstallation from local repository copy:\n```bash\ngit clone https://github.com/mad-lab-fau/hpc-helper.git\ncd hpc_helper\npip install .\n```\n",
    'author': 'Robert Richer',
    'author_email': 'robert.richer@fau.de',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/mad-lab-fau/hpc-helper',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.7.1,<3.10',
}


setup(**setup_kwargs)
