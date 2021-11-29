# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['piicatcher']

package_data = \
{'': ['*']}

install_requires = \
['click',
 'commonregex>=1.5,<2.0',
 'dbcat>=0.10.0,<0.11.0',
 'python-json-logger>=2.0.2,<3.0.0',
 'pyyaml',
 'spacy',
 'tabulate>=0.8.9,<0.9.0',
 'tqdm>=4.62.3,<5.0.0',
 'typer>=0.4.0,<0.5.0']

extras_require = \
{':python_version >= "3.6" and python_version < "3.7"': ['dataclasses>=0.6'],
 'datahub': ['great-expectations>=0.13.42,<0.14.0',
             'acryl-datahub>=0.8.16,<0.9.0']}

entry_points = \
{'console_scripts': ['piicatcher = piicatcher.command_line:app']}

setup_kwargs = {
    'name': 'piicatcher',
    'version': '0.18.1',
    'description': 'Find PII data in databases',
    'long_description': '[![piicatcher](https://github.com/tokern/piicatcher/actions/workflows/ci.yml/badge.svg)](https://github.com/tokern/piicatcher/actions/workflows/ci.yml)\n[![PyPI](https://img.shields.io/pypi/v/piicatcher.svg)](https://pypi.python.org/pypi/piicatcher)\n[![image](https://img.shields.io/pypi/l/piicatcher.svg)](https://pypi.org/project/piicatcher/)\n[![image](https://img.shields.io/pypi/pyversions/piicatcher.svg)](https://pypi.org/project/piicatcher/)\n[![image](https://img.shields.io/docker/v/tokern/piicatcher)](https://hub.docker.com/r/tokern/piicatcher)\n\n# PII Catcher for Databases and Data Warehouses\n\n## Overview\n\nPIICatcher is a scanner for PII and PHI information. It finds PII data in your databases and file systems\nand tracks critical data. PIICatcher uses two techniques to detect PII:\n\n* Match regular expressions with column names\n* Match regular expressions and using NLP libraries to match sample data in columns.\n\nRead more in the [blog post](https://tokern.io/blog/scan-pii-data-warehouse/) on both these strategies.\n\nPIICatcher is *battery-included* with a growing set of\nregular expressions for scanning column names as well as data. It also include [Spacy](https://spacy.io).\n\nPIICatcher supports incremental scans and will only scan new or not-yet scanned columns. Incremental scans allow easy\nscheduling of scans. It also provides powerful options to include or exclude schema and tables to manage compute resources.\n\nThere are ingestion functions for both [Datahub](https://datahubproject.io) and [Amundsen](https://amundsen.io) which will tag columns \nand tables with PII and the type of PII tags.\n\n![PIIcatcher Screencast](https://user-images.githubusercontent.com/1638298/143765818-87c7059a-f971-447b-83ca-e21182e28051.gif)\n\n\n## Resources\n\n* [AWS Glue & Lake Formation Privilege Analyzer](https://tokern.io/blog/lake-glue-access-analyzer/) for an example of how piicatcher is used in production.\n* [Two strategies to scan data warehouses](https://tokern.io/blog/scan-pii-data-warehouse/)\n\n## Quick Start\n\nPIICatcher is available as a docker image or command-line application.\n\n### Command-line\nTo install use pip:\n\n    python3 -m venv .env\n    source .env/bin/activate\n    pip install piicatcher\n\n    # Install Spacy English package\n    python -m spacy download en_core_web_sm\n    \n    # run piicatcher on a sqlite db and print report to console\n    piicatcher scan sqlite --path \'/db/sqlqb\'\n    ╭─────────────┬─────────────┬─────────────┬─────────────╮\n    │   schema    │    table    │   column    │   has_pii   │\n    ├─────────────┼─────────────┼─────────────┼─────────────┤\n    │        main │    full_pii │           a │           1 │\n    │        main │    full_pii │           b │           1 │\n    │        main │      no_pii │           a │           0 │\n    │        main │      no_pii │           b │           0 │\n    │        main │ partial_pii │           a │           1 │\n    │        main │ partial_pii │           b │           0 │\n    ╰─────────────┴─────────────┴─────────────┴─────────────╯\n\n\n### API\n    from piicatcher.api import scan_postgresql\n\n    # PIICatcher uses a catalog to store its state. \n    # The easiest option is to use a sqlite memory database.\n    # For production usage check, https://tokern.io/docs/data-catalog\n    catalog_params={\'catalog_path\': \':memory:\'}\n    output = scan_postrgresql(catalog_params=catalog_params, name="pg_db", uri="127.0.0.1", \n                              username="piiuser", password="p11secret", database="piidb", \n                              include_table_regex=["sample"])\n    print(output)\n\n    # Example Output\n    [[\'public\', \'sample\', \'gender\', \'PiiTypes.GENDER\'], \n     [\'public\', \'sample\', \'maiden_name\', \'PiiTypes.PERSON\'], \n     [\'public\', \'sample\', \'lname\', \'PiiTypes.PERSON\'], \n     [\'public\', \'sample\', \'fname\', \'PiiTypes.PERSON\'], \n     [\'public\', \'sample\', \'address\', \'PiiTypes.ADDRESS\'], \n     [\'public\', \'sample\', \'city\', \'PiiTypes.ADDRESS\'], \n     [\'public\', \'sample\', \'state\', \'PiiTypes.ADDRESS\'], \n     [\'public\', \'sample\', \'email\', \'PiiTypes.EMAIL\']]\n\n\n## Supported Databases\n\nPIICatcher supports the following databases:\n1. **Sqlite3** v3.24.0 or greater\n2. **MySQL** 5.6 or greater\n3. **PostgreSQL** 9.4 or greater\n4. **AWS Redshift**\n5. **AWS Athena**\n6. **Snowflake**\n\n## Documentation\n\nFor advanced usage refer documentation [PIICatcher Documentation](https://tokern.io/docs/piicatcher).\n\n## Survey\n\nPlease take this [survey](https://forms.gle/Ns6QSNvfj3Pr2s9s6) if you are a user or considering using PIICatcher. \nThe responses will help to prioritize improvements to the project.\n\n## Contributing\n\nFor Contribution guidelines, [PIICatcher Developer documentation](https://tokern.io/docs/piicatcher/development). \n\n',
    'author': 'Tokern',
    'author_email': 'info@tokern.io',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://tokern.io/',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<3.9',
}


setup(**setup_kwargs)
