# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['lpsd']

package_data = \
{'': ['*']}

install_requires = \
['numpy>=1.18,<2.0', 'pandas>=1.0,<2.0', 'scipy>=1.5,<2.0']

extras_require = \
{':python_version <= "3.7"': ['importlib-metadata>=1.1.3,<2.0.0']}

setup_kwargs = {
    'name': 'lpsd',
    'version': '0.2.0',
    'description': 'Python and C implementation for logarithmical power spectral density (LPSD) calculation.',
    'long_description': '# Python 3 LPSD algorithm\n\n## Overview\n\nThis repository contains a Python 3 implementation of the LPSD algorithm.\nThe implementation is similiar to the LPSD implementation in the Matlab package LTPDA.\nThe core of the algorithm can be run as Python 3 or as (faster) C code.\nBoth deliver the *same results*.\nTo run the C core the file ltpda_dft.c has to be compiled to a shared library.\n\n\n## Installation\n\nInstall directly with pip:\n```bash\npip install lpsd\n```\n\n\n## Usage\n\nFully working examples can be found in [/doc/examples](https://git.physnet.uni-hamburg.de/gwd/lpsd/-/tree/main/doc/examples).\n\n### With a DataFrame\n\nRecommended interface, direct usage of a `DataFrame`\n\n```python\nimport pandas as pd\nfrom lpsd import lpsd\n# read time series\ndata = pd.read_csv("time_series.csv.gz", index_col=0)\n# select column and calculate\nspectrum = lpsd(data["column"])\n# plot PSD\nspectrum["psd"].plot(logx=True, logy=True)\n```\n\n### Using numpy arrays\n\nUse the traditional method `lpsd_trad`, which uses simple numpy arrays.\n\n\n## References\n\n- [Improved spectrum estimation from digitized time series on a logarithmic frequency axis](https://doi.org/10.1016/j.measurement.2005.10.010)\nAuthors: Michael Tröbs and Gerhard Heinzel\n- [Spectrum and spectral density estimation by the Discrete Fourier transform (DFT), including a comprehensive list of window functions and some new flat-top windows](http://hdl.handle.net/11858/00-001M-0000-0013-557A-5)\nAuthors: Gerhard Heinzel, Albrecht Rüdiger and Roland Schilling\n- [MATLAB Toolbox LTPDA](https://www.elisascience.org/ltpda/)\nAuthor:  Martin Hewitson\n',
    'author': 'Christian Darsow-Fromm',
    'author_email': 'cdarsowf@physnet.uni-hamburg.de',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://gitlab.com/gwd/lpsd',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.7.1,<3.11',
}


setup(**setup_kwargs)
