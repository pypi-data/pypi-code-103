# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['kilroyplot', 'kilroyplot.resources']

package_data = \
{'': ['*']}

install_requires = \
['appdirs>=1.4,<2.0', 'matplotlib>=3.5,<4.0']

extras_require = \
{'dev': ['jupyterlab>=3,<4', 'pytest>=6,<7'], 'test': ['pytest>=6,<7']}

setup_kwargs = {
    'name': 'kilroyplot',
    'version': '0.1.0',
    'description': 'kilroy plot styling 📊',
    'long_description': '<h1 align="center">kilroyplot</h1>\n\n<div align="center">\n\n[![Running tests](https://github.com/kilroybot/kilroyplot/actions/workflows/test.yml/badge.svg)](https://github.com/kilroybot/kilroyplot/actions/workflows/test.yml)\n\n</div>\n\n---\n\nkilroy plot styling 📊\n\n## Installing\n\nUsing `pip`:\n\n```sh\npip install kilroyplot\n```\n\n## Usage\n\nJust import and use the same as with `matplotlib`:\n\n```python\nfrom kilroyplot.plot import plt\n```\n',
    'author': 'kilroy',
    'author_email': 'kilroymail@pm.me',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/kilroybot/kilroyplot',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
