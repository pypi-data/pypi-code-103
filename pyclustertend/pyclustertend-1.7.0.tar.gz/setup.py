# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pyclustertend']

package_data = \
{'': ['*']}

install_requires = \
['matplotlib>=3.3.3,<4.0.0',
 'numba>=0.54.1,<0.55.0',
 'numpy==1.20.3',
 'pandas>=1.2.0,<2.0.0',
 'scikit-learn>=0.24.0,<0.25.0']

setup_kwargs = {
    'name': 'pyclustertend',
    'version': '1.7.0',
    'description': 'A package to assess cluster tendency for unsupervised learning',
    'long_description': '# pyclustertend\n\n\n\n\n\n\n[![Build Status](https://travis-ci.com/lachhebo/pyclustertend.svg?branch=master)](https://travis-ci.com/lachhebo/pyclustertend)  [![PyPi Status](https://img.shields.io/pypi/v/pyclustertend.svg?color=brightgreen)](https://pypi.org/project/pyclustertend/) [![Documentation Status](https://readthedocs.org/projects/pyclustertend/badge/?version=master)](https://pyclustertend.readthedocs.io/en/master/) [![Downloads](https://pepy.tech/badge/pyclustertend)](https://pepy.tech/project/pyclustertend) [![codecov](https://codecov.io/gh/lachhebo/pyclustertend/branch/master/graph/badge.svg)](https://codecov.io/gh/lachhebo/pyclustertend)\n[![DOI](https://zenodo.org/badge/187477036.svg)](https://zenodo.org/badge/latestdoi/187477036)\n\npyclustertend is a python package specialized in cluster tendency. Cluster tendency consist to assess if clustering algorithms are relevant for a dataset.\n\nThree methods for assessing cluster tendency are currently implemented and one additional method based on metrics obtained with a KMeans estimator :\n\n\n\n- [x] Hopkins Statistics\n- [x] VAT\n- [x] iVAT\n\n- [x] Metric based method (silhouette, calinksi, davies bouldin)\n\n## Installation\n\n```shell\n    pip install pyclustertend\n```\n\n## Usage\n\n### Example Hopkins\n\n```python\n    >>>from sklearn import datasets\n    >>>from pyclustertend import hopkins\n    >>>from sklearn.preprocessing import scale\n    >>>X = scale(datasets.load_iris().data)\n    >>>hopkins(X,150)\n    0.18950453452838564\n```\n\n### Example VAT\n\n```python\n    >>>from sklearn import datasets\n    >>>from pyclustertend import vat\n    >>>from sklearn.preprocessing import scale\n    >>>X = scale(datasets.load_iris().data)\n    >>>vat(X)\n```\n\n<img height="350" src="https://raw.githubusercontent.com/lachhebo/pyclustertend/screenshots/vat.png" />\n\n### Example iVat\n\n```python\n    >>>from sklearn import datasets\n    >>>from pyclustertend import ivat\n    >>>from sklearn.preprocessing import scale\n    >>>X = scale(datasets.load_iris().data)\n    >>>ivat(X)\n```\n\n<img height="350" src="https://raw.githubusercontent.com/lachhebo/pyclustertend/screenshots/ivat.png" />\n\n## Notes\n\nIt\'s preferable to scale the data before using hopkins or vat algorithm as they use distance between observations. Moreover, vat and ivat algorithms\ndo not really fit to massive databases. A first solution is to sample the data before using those algorithms. \n',
    'author': 'Ismaïl Lachheb',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/lachhebo/pyclustertend',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<3.10',
}


setup(**setup_kwargs)
