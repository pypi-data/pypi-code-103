# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['plotly_resampler', 'plotly_resampler.downsamplers']

package_data = \
{'': ['*']}

install_requires = \
['dash-bootstrap-components>=0.13.1,<0.14.0',
 'dash>=2.0.0,<3.0.0',
 'jupyter-dash>=0.4.0,<0.5.0',
 'lttbc>=0.2.0,<0.3.0',
 'orjson>=3.6.4,<4.0.0',
 'plotly>=5.3.1,<6.0.0',
 'trace-updater>=0.0.3,<0.0.4']

setup_kwargs = {
    'name': 'plotly-resampler',
    'version': '0.2.0',
    'description': 'Visualizing large time series with plotly',
    'long_description': None,
    'author': 'Jonas Van Der Donckt',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<3.10',
}


setup(**setup_kwargs)
