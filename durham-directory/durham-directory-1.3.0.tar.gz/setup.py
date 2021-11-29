# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['durham_directory']

package_data = \
{'': ['*']}

install_requires = \
['bs4>=0.0.1,<0.0.2', 'lxml>=4.6.3,<5.0.0', 'requests>=2.26.0,<3.0.0']

entry_points = \
{'console_scripts': ['durham-directory = durham_directory:main']}

setup_kwargs = {
    'name': 'durham-directory',
    'version': '1.3.0',
    'description': 'Python Bindings for the Durham University (UK) Directory',
    'long_description': '# Python bindings for the Durham University (UK) Directory\n\nThis package provides basic python bindings for [the Durham University\nDirectory](https://dur.ac.uk/directory/password), where Durham University\nstudents and staff can look up fellow students and staff.\n\nIt is nothing more than a wrapper around `requests` and `bs4`, and absolutely\nnothing clever is being done (although I do think the code is pleasantly\nsimple).\n\n## Installation\n\n```bash\npython -m pip install durham-directory\n```\n\n## CLI Usage\n\n```bash\ndurham-directory --help\ndurham-directory --oname John --surname Morris\n```\n\n## API Usage\n\n```python\nfrom durham_directory import Query\nquery = Query(username="me") # will prompt for password when evaluated\nquery(oname="John", surname="Morris", type_="any")\n```\n\nOr if you want to choose one result:\n\n```python\nfrom durham_directory import QueryOne\nquery = QueryOne()\nquery(oname="John", surname="Morris", type_="any")\n```\n\nWe use fuzzy string matching via `fuzzywuzzy` (ignoring the title) to sort\nresults, as Durham appears to return them bogosorted.\n\n## Scripts\n\nAn example script parsing a csv extracted from the spreadsheets it seems\ntimetabling send around and printing Org-mode tables is in `parse_csv.py`.\n',
    'author': 'John Maximilian',
    'author_email': '2e0byo@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/2e0byo/durham-directory',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
