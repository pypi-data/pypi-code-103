# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['aiopvpc']

package_data = \
{'': ['*'], 'aiopvpc': ['pvpcbill/*']}

install_requires = \
['aiohttp>=3.7.4.post0', 'async_timeout>=3.0.1', 'holidays>0.11.1']

extras_require = \
{':python_version < "3.9"': ['backports.zoneinfo>=0.2.1,<0.3.0'],
 'jupyter': ['jupyter', 'pandas', 'matplotlib']}

setup_kwargs = {
    'name': 'aiopvpc',
    'version': '2.2.5rc1',
    'description': 'Retrieval of Spanish Electricity hourly prices (PVPC)',
    'long_description': '[![PyPI Version][pypi-image]][pypi-url]\n[![pre-commit.ci Status][pre-commit-ci-image]][pre-commit-ci-url]\n[![Build Status][build-image]][build-url]\n[![Code Coverage][coverage-image]][coverage-url]\n<!-- Badges -->\n[pypi-image]: https://img.shields.io/pypi/v/aiopvpc\n[pypi-url]: https://pypi.org/project/aiopvpc/\n[pre-commit-ci-image]: https://results.pre-commit.ci/badge/github/azogue/aiopvpc/master.svg\n[pre-commit-ci-url]: https://results.pre-commit.ci/latest/github/azogue/aiopvpc/master\n[build-image]: https://github.com/azogue/aiopvpc/actions/workflows/main.yml/badge.svg\n[build-url]: https://github.com/azogue/aiopvpc/actions/workflows/main.yml\n[coverage-image]: https://codecov.io/gh/azogue/aiopvpc/branch/master/graph/badge.svg\n[coverage-url]: https://codecov.io/gh/azogue/aiopvpc\n\n# aiopvpc\n\nSimple aio library to download Spanish electricity hourly prices.\n\nMade to support the [**`pvpc_hourly_pricing`** HomeAssistant integration](https://www.home-assistant.io/integrations/pvpc_hourly_pricing/).\n\n<span class="badge-buymeacoffee"><a href="https://www.buymeacoffee.com/azogue" title="Donate to this project using Buy Me A Coffee"><img src="https://img.shields.io/badge/buy%20me%20a%20coffee-donate-yellow.svg" alt="Buy Me A Coffee donate button" /></a></span>\n\n\n## Install\n\nInstall with `pip install aiopvpc` or clone it to run tests or anything else.\n\n## Usage\n\n```python\nfrom datetime import datetime\nfrom aiopvpc import PVPCData\n\npvpc_handler = PVPCData(tariff="discrimination", zone_ceuta_melilla=False)\n\nstart = datetime(2021, 5, 20, 22)\nend = datetime(2021, 6, 7, 16)\nprices_range: dict = await pvpc_handler.async_download_prices_for_range(start, end)\n```\n\nCheck [this example on a jupyter notebook](https://github.com/azogue/aiopvpc/blob/master/Notebooks/Download%20PVPC%20prices.ipynb), where the downloader is combined with pandas and matplotlib to plot the electricity prices.\nTo play with it, clone the repo and install the project with `poetry install -E jupyter`, and then `poetry run jupyter notebook`.\n\n![sample_pvpc_plot.png](https://github.com/azogue/aiopvpc/blob/master/Notebooks/sample_pvpc_plot.png)\n',
    'author': 'Eugenio Panadero',
    'author_email': 'eugenio.panadero@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/azogue/aiopvpc',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
