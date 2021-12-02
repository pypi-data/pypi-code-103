# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['hfurl']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'hfurl',
    'version': '0.1.0',
    'description': 'Human-friendly URL parsing in python',
    'long_description': '<h1>HFURL - Human-friendly URL</h1>\n\nThis is a tiny python library taht provides parsing for human-firendly.\nCompletely disregarding RFC it correctly parses url with no schema\n(eg. `example.com` is equivalent to `https://example.com/`).\n\nUseful when reading input URL from user, who as we al know, often omit schema.\n\n## Usage\n\n```python\nfrom hfurl import parse_url\n\nurl = parse_url("example.com:443/about")\nassert url.host == "example.com"\n```\n',
    'author': 'Crystal Melting Dot',
    'author_email': 'stresspassing@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/cmd410/hfurl',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
