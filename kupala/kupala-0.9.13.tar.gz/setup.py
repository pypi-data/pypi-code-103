# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['kupala', 'kupala.disks', 'kupala.ext']

package_data = \
{'': ['*'], 'kupala': ['templates/errors/*']}

install_requires = \
['Jinja2>=3.0.2,<4.0.0',
 'deesk>=0.1.0,<0.2.0',
 'imia>=0.3.1,<0.4.0',
 'python-dotenv>=0.19.1,<0.20.0',
 'python-multipart>=0.0.5,<0.0.6',
 'starlette>=0.17.0,<0.18.0',
 'starsessions>=1.1.5,<2.0.0']

extras_require = \
{'s3': ['aioboto3>=9.2.2,<10.0.0']}

setup_kwargs = {
    'name': 'kupala',
    'version': '0.9.13',
    'description': 'A modern web framework for Python.',
    'long_description': '# Kupala Framework\n\nA modern web framework for Python.\n\n![PyPI](https://img.shields.io/pypi/v/kupala)\n![GitHub Workflow Status](https://img.shields.io/github/workflow/status/alex-oleshkevich/kupala/Lint)\n![GitHub](https://img.shields.io/github/license/alex-oleshkevich/kupala)\n![Libraries.io dependency status for latest release](https://img.shields.io/librariesio/release/pypi/kupala)\n![PyPI - Downloads](https://img.shields.io/pypi/dm/kupala)\n![GitHub Release Date](https://img.shields.io/github/release-date/alex-oleshkevich/kupala)\n![Lines of code](https://img.shields.io/tokei/lines/github/alex-oleshkevich/kupala)\n\n## Installation\n\nInstall `kupala` using PIP or poetry:\n\n```bash\npip install kupala\n# or\npoetry add kupala\n```\n\n## Features\n\n-   TODO\n\n## Quick start\n\nSee example application in `examples/` directory of this repository.\n',
    'author': 'Alex Oleshkevich',
    'author_email': 'alex.oleshkevich@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/alex-oleshkevich/kupala',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.9.0,<4.0.0',
}


setup(**setup_kwargs)
