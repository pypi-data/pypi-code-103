# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['fact_explorer',
 'fact_explorer.app',
 'fact_explorer.app.db',
 'fact_explorer.app.entities',
 'fact_explorer.app.frontend',
 'fact_explorer.cli']

package_data = \
{'': ['*'],
 'fact_explorer.app.frontend': ['static/*',
                                'templates/*',
                                'templates/fragments/*']}

install_requires = \
['aiofiles>=0.6.0,<0.7.0',
 'asyncpg>=0.22.0,<0.23.0',
 'cryptoshred>=0.0.6,<0.0.7',
 'fastapi>=0.65.0,<0.66.0',
 'psycopg2-binary>=2.8.6,<3.0.0',
 'rich>=10.4.0,<11.0.0',
 'typer>=0.3.2,<0.4.0',
 'uvicorn>=0.13.4,<0.14.0']

extras_require = \
{'docs': ['sphinx-rtd-theme>=0.5.2,<0.6.0',
          'sphinx-click>=3.0.1,<4.0.0',
          'Sphinx<4']}

entry_points = \
{'console_scripts': ['fact-explorer = fact_explorer.cli.main:app']}

setup_kwargs = {
    'name': 'fact-explorer',
    'version': '0.0.3',
    'description': 'A fast and simple tool to explore facts.',
    'long_description': "# Fact Explorer\n\nWelcome to fact_explorer. You can find more extensive documentation over at [readthedocs](https://fact-explorer.readthedocs.io/en/latest/).\n\nThis project arose manly out of the necessity to work with events directly instead of through projections. This is useful to:\n\n- Enable searching for 'random' events quickly during debugging\n- Checking events during migrations\n- Many other things (you should probably not do if you are an event purist)\n\nContributions are welcome. Just get in touch.\n\n## Quickstart\n\nSimply `pip install fact-exporter` and get going. The cli is available as `fact-exporter` and\nyou can run `fact-exporter --help` to get up to speed on what you can do.\n\n## Development\n\nThis project uses `poetry` for dependency management and `pre-commit` for local checks.\n",
    'author': 'Eduard Thamm',
    'author_email': 'eduard.thamm@thammit.at',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://gitlab.com/edthamm/fact-explorer',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
