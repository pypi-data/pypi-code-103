# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['fal',
 'faldbt',
 'faldbt.cp',
 'faldbt.cp.contracts',
 'faldbt.cp.contracts.graph',
 'faldbt.cp.parser',
 'faldbt.cp.task',
 'faldbt.utils']

package_data = \
{'': ['*']}

install_requires = \
['Jinja2>=2.11.3,<3.0.0',
 'PyYAML>=6.0,<7.0',
 'agate-sql>=0.5.8,<0.6.0',
 'arrow>=1.2.0,<2.0.0',
 'click>=8.0.3,<9.0.0',
 'dbt-bigquery>=0.21.0,<0.22.0',
 'dbt>=0.21.0,<0.22.0',
 'firebase-admin>=5.1.0,<6.0.0',
 'google-cloud-bigquery-storage>=2.9.1,<3.0.0',
 'google-cloud-bigquery>=2.28.1,<3.0.0',
 'ninja>=1.10.2,<2.0.0',
 'pandas>=1.3.4,<2.0.0',
 'pyarrow>=5.0.0,<6.0.0',
 'pydantic>=1.8.2,<2.0.0']

entry_points = \
{'console_scripts': ['fal = fal.cli:cli']}

setup_kwargs = {
    'name': 'fal',
    'version': '0.1.30',
    'description': 'fal allows you to run python scripts directly from your dbt project.',
    'long_description': None,
    'author': 'Meder Kamalov',
    'author_email': 'meder@fal.ai',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7.1,<3.11',
}


setup(**setup_kwargs)
