# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['escapyde', 'escapyde.examples']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'escapyde',
    'version': '0.1.1',
    'description': 'Yet another ANSI escape sequence library for Python - now modernised!',
    'long_description': '# escapyde\n\nYet another ANSI escape sequence library for Python - now modernised!\n\n## Installation\n\nThe package is readily available on PyPI. There are no dependencies, but Python 3.6 or newer is required.\n\nOn Windows:\n\n```sh\npy -m pip install escapyde\n```\n\nOn other platforms:\n\n```sh\npip3 install escapyde\n```\n\n## Usage\n\n```py\nimport escapyde\nfrom escapyde.examples.text import SKULL\n\nsome_text = "Hello, world!"\n\nprint(f"I want to print this red: {escapyde.FRED | some_text}, and this yellow: {escapyde.FYELLOW | \'Hi!\'}.")\n\nprint(f"Here\'s a cyan skull:\\n{escapyde.FCYAN | SKULL}")\n```\n\nAs can be seen, the example works perfectly fine:\n\n![A screenshot of the example run on IPython on Windows.](./docs/readme_screenshot.png "Not bad, not bad at all.")\n',
    'author': 'Lari Liuhamo',
    'author_email': 'lari.liuhamo+pypi@gmail.com',
    'maintainer': 'Lari Liuhamo',
    'maintainer_email': 'lari.liuhamo+pypi@gmail.com',
    'url': 'https://pypi.org/project/escapyde/',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
