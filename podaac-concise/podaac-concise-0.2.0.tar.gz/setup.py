# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['podaac', 'podaac.merger', 'podaac.merger.harmony']

package_data = \
{'': ['*']}

install_requires = \
['harmony-service-lib>=1.0.9,<2.0.0',
 'importlib-metadata>=4.8.1,<5.0.0',
 'netCDF4>=1.5.6,<2.0.0',
 'numpy>=1.20.3,<2.0.0']

entry_points = \
{'console_scripts': ['benchmark = stress_test.benchmark:main',
                     'concise_harmony = podaac.merger.harmony.cli:main',
                     'merge = podaac.merger.merge_cli:main']}

setup_kwargs = {
    'name': 'podaac-concise',
    'version': '0.2.0',
    'description': 'Harmony service that merges granules',
    'long_description': '# CONCISE (CONCatenatIon SErvice)\n\n[![Coverage](https://sonarcloud.io/api/project_badges/measure?project=podaac_concise&metric=coverage)](https://sonarcloud.io/dashboard?id=podaac_concise)  \ndevelop: [![Develop Build](https://github.com/podaac/concise/actions/workflows/build-pipeline.yml/badge.svg?branch=develop)](https://github.com/podaac/concise/actions/workflows/build-pipeline.yml)  \nmain: [![Main Build](https://github.com/podaac/concise/actions/workflows/build-pipeline.yml/badge.svg?branch=main&event=push)](https://github.com/podaac/concise/actions/workflows/build-pipeline.yml)\n\n\nHarmony service for concatenating L2 data.\n\nIf you would like to contribute to Concise, refer to the [contribution document](CONTRIBUTING.md).\n\n## How to test Concise locally\n\nThere are comprehensive unit tests for Concise. The tests can be run as follows:\n\n```shell script\npoetry run pytest tests/\n```\n\n',
    'author': 'podaac-tva',
    'author_email': 'podaac-tva@jpl.nasa.gov',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/podaac/concise',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
