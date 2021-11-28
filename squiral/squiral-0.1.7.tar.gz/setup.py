# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['squiral']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'squiral',
    'version': '0.1.7',
    'description': 'squiral - square spiral',
    'long_description': '# squiral\n[![](https://img.shields.io/pypi/v/squiral)](https://pypi.org/project/squiral/)\n[![made-with-python](https://img.shields.io/badge/Made%20with-Python-1f425f.svg)](https://www.python.org/)\n[![](https://img.shields.io/pypi/pyversions/squiral.svg)](https://pypi.org/project/squiral/)<br/>\n[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/sadikkuzu/squiral/main.svg)](https://results.pre-commit.ci/latest/github/sadikkuzu/squiral/main)\n[![Python lint&test](https://github.com/sadikkuzu/squiral/actions/workflows/python-package.yml/badge.svg)](https://github.com/sadikkuzu/squiral/actions/workflows/python-package.yml)\n[![Publish Python Package](https://github.com/sadikkuzu/squiral/actions/workflows/python-publish.yml/badge.svg)](https://github.com/sadikkuzu/squiral/actions/workflows/python-publish.yml)\n\n**squ**are sp**iral**\n\n```\nWelcome to Squiral!\nHere is an example:\n21 22 23 24 25\n20  7  8  9 10\n19  6  1  2 11\n18  5  4  3 12\n17 16 15 14 13\n```\n\nThe basic idea behind printing this matrix is<br/>\nto start from the middle of the matrix and then moving:<br/>\n`right` >> `down` >> `left` >> `up`<br/>\nand not returning to the same row again.\n\n### Install\n\n`pip install squiral`\n\n#### Usage\n\n```python\n>>> import squiral as sq\n>>> sq.printout(sq.produce(5))\n21 22 23 24 25\n20  7  8  9 10\n19  6  1  2 11\n18  5  4  3 12\n17 16 15 14 13\n>>>\n```\n',
    'author': 'SADIK KUZU',
    'author_email': 'sadikkuzu@hotmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/sadikkuzu/squiral',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
