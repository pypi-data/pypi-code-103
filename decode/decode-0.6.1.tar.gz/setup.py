# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['decode', 'decode.core', 'decode.core.array', 'decode.core.cube']

package_data = \
{'': ['*'], 'decode': ['data/*']}

install_requires = \
['astropy>=4.3,<5.0',
 'matplotlib>=3.2,<4.0',
 'netcdf4>=1.5,<2.0',
 'numpy>=1.19,<2.0',
 'scikit-learn>=1.0,<2.0',
 'scipy>=1.4,<2.0',
 'tomli>=1.2,<2.0',
 'tqdm>=4.62,<5.0',
 'xarray>=0.18,<0.19']

setup_kwargs = {
    'name': 'decode',
    'version': '0.6.1',
    'description': 'DESHIMA code for data analysis',
    'long_description': '# De:code\n\n[![PyPI](https://img.shields.io/pypi/v/decode.svg?label=PyPI&style=flat-square)](https://pypi.org/pypi/decode/)\n[![Python](https://img.shields.io/pypi/pyversions/decode.svg?label=Python&color=yellow&style=flat-square)](https://pypi.org/pypi/decode/)\n[![Test](https://img.shields.io/github/workflow/status/deshima-dev/decode/Test?logo=github&label=Test&style=flat-square)](https://github.com/deshima-dev/decode/actions)\n[![License](https://img.shields.io/badge/license-MIT-blue.svg?label=License&style=flat-square)](LICENSE)\n[![DOI](https://img.shields.io/badge/DOI-10.5281/zenodo.3384216-blue?style=flat-square)](https://doi.org/10.5281/zenodo.3384216)\n\nDESHIMA code for data analysis\n\n## Installation\n\n```shell\n$ pip install decode\n```\n',
    'author': 'Akio Taniguchi',
    'author_email': 'taniguchi@a.phys.nagoya-u.ac.jp',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/deshima-dev/decode/',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<3.10',
}


setup(**setup_kwargs)
