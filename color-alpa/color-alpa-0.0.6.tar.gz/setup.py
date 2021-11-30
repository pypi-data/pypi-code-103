# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['color']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'color-alpa',
    'version': '0.0.6',
    'description': 'Test skeleton project for displaying ANSI color',
    'long_description': '# Color\n\nSimple test skeleton project\n\n## Usage\n\n```\nfrom color import Color\n\nansi_text_in_green = Color.green("text in green")\nansi_text_in_blue = Color.blue("text in blue")\n```',
    'author': 'Albert Pang',
    'author_email': 'alpaalpa@mac.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/alpaalpa/color',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
