# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['db_contrib_tool', 'db_contrib_tool.setup_repro_env', 'db_contrib_tool.utils']

package_data = \
{'': ['*'], 'db_contrib_tool': ['config/*']}

install_requires = \
['PyGithub>=1.55,<2.0',
 'PyYAML>=6.0,<7.0',
 'analytics-python>=1.4.0,<2.0.0',
 'distro>=1.6.0,<2.0.0',
 'evergreen.py>=3.3.9,<4.0.0',
 'packaging>=21.3,<22.0',
 'requests>=2.26.0,<3.0.0',
 'structlog>=21.2.0,<22.0.0']

entry_points = \
{'console_scripts': ['db-contrib-tool = db_contrib_tool.cli:main']}

setup_kwargs = {
    'name': 'db-contrib-tool',
    'version': '0.1.0',
    'description': "The `db-contrib-tool` - MongoDB's tool for contributors.",
    'long_description': None,
    'author': 'STM team',
    'author_email': 'dev-prod-stm@10gen.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
