# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['terminaltables']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'terminaltables',
    'version': '3.1.6',
    'description': 'Generate simple tables in terminals from a nested list of strings. (has wheels!)',
    'long_description': "## terminaltables\n\nForked because original project's repo is ARCHIVED and there are no wheels for the old project in pypi.\n\n# What is it\n\nEasily draw tables in terminal/console applications from a list of lists of strings. Supports multi-line rows.\n\n- Python 2.6, 2.7, PyPy, PyPy3, 3.3, 3.4, and 3.5 supported on Linux and OS X.\n- Python 2.7, 3.3, 3.4, and 3.5 supported on Windows (both 32 and 64 bit versions of Python).\n\n📖 Full documentation: https://robpol86.github.io/terminaltables\n\n\nQuickstart\n==========\n\nInstall:\n\n```bash\npip install terminaltables\n```\n\nUsage:\n\n```python\nfrom terminaltables import AsciiTable\ntable_data = [\n    ['Heading1', 'Heading2'],\n    ['row1 column1', 'row1 column2'],\n    ['row2 column1', 'row2 column2'],\n    ['row3 column1', 'row3 column2']\n]\ntable = AsciiTable(table_data)\nprint table.table\n```\n```bash\n+--------------+--------------+\n| Heading1     | Heading2     |\n+--------------+--------------+\n| row1 column1 | row1 column2 |\n| row2 column1 | row2 column2 |\n| row3 column1 | row3 column2 |\n+--------------+--------------+\n```\n\nExample Implementations\n=======================\n[Example Scripts Screenshot](docs/examples.png?raw=true)\n\nSource code for examples: \n[example1.py](https://github.com/Robpol86/terminaltables/blob/master/example1.py)\n`example2.py <https://github.com/Robpol86/terminaltables/blob/master/example2.py>`_, and\n`example3.py <https://github.com/Robpol86/terminaltables/blob/master/example3.py>`_\n\n.. changelog-section-start\n",
    'author': 'Robpol86',
    'author_email': 'robpol86@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/matthewdeanmartin/terminaltables',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=2.6',
}


setup(**setup_kwargs)
