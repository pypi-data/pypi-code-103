# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['dbt_superset_lineage']

package_data = \
{'': ['*']}

install_requires = \
['pathlib>=1.0.1,<2.0.0',
 'requests>=2.26.0,<3.0.0',
 'ruamel.yaml>=0.17.17,<0.18.0',
 'sqlfluff>=0.8.2,<0.9.0',
 'typer>=0.4.0,<0.5.0']

entry_points = \
{'console_scripts': ['dbt-superset-lineage = '
                     'dbt_superset_lineage.__init__:app']}

setup_kwargs = {
    'name': 'dbt-superset-lineage',
    'version': '0.1.0',
    'description': 'A package for extracting dashboards from Apache Superset to dbt docs as exposures.',
    'long_description': '# dbt-superset-lineage',
    'author': 'Michal Kolacek',
    'author_email': 'mkolacek@slido.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
