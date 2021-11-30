# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['verdandi']

package_data = \
{'': ['*']}

entry_points = \
{'console_scripts': ['verdandi = verdandi.main:main']}

setup_kwargs = {
    'name': 'verdandi',
    'version': '0.2.2',
    'description': 'Benchmarking framework',
    'long_description': '<p align="center">\n    <img src="https://raw.githubusercontent.com/exler/verdandi/main/docs/logo.png" width="192">\n</p>\n<p align="center">\n    Class-based benchmarking framework with <code>unittest</code>-style behavior \n</p>\n<p align="center">\n    <img src="https://github.com/exler/verdandi/actions/workflows/quality.yml/badge.svg">\n</p>\n\n## Overview\n\nVerdandi is a small library providing class-based benchmarking functionality with similar interface to Python\'s [unittest](https://docs.python.org/3/library/unittest.html).\n\n## Requirements\n\n* Python >= 3.6\n\n## Installation\n```\n$ pip install verdandi\n```\n\n## Usage\n\nVerdandi can be used as a command-line both by passing the files containing benchmarks as arguments or by using the discovery functionality:\n\n```bash\n# Specifying the files\n$ verdandi tests.benchmarks.bench_module1 tests.benchmarks.bench_module2\n\n# Running discovery\n$ verdandi\n```\n\n## Credits\n\n* [unittest](https://docs.python.org/3/library/unittest.html) - Verdandi is based on `unittest` and wouldn\'t exist without it!\n* [pytest](https://docs.pytest.org/en/6.2.x/) - some improvements over the `unittest` library are inspired by `pytest` or its plugins!\n\n## License\n\nCopyright (c) 2021 by ***Kamil Marut***\n\n`verdandi` is under the terms of the [MIT License](https://www.tldrlegal.com/l/mit), following all clarifications stated in the [license file](LICENSE).\n',
    'author': 'Kamil Marut',
    'author_email': 'kamil@kamilmarut.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/exler/verdandi',
    'packages': packages,
    'package_data': package_data,
    'entry_points': entry_points,
    'python_requires': '>=3.6.2,<4.0',
}


setup(**setup_kwargs)
