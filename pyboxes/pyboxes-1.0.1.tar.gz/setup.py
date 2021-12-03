# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['pyboxes', 'pyboxes.commands']

package_data = \
{'': ['*']}

install_requires = \
['click>=8.0.1,<9.0.0', 'loguru>=0.5.3,<0.6.0']

entry_points = \
{'console_scripts': ['pybox = pyboxes.__main__:main']}

setup_kwargs = {
    'name': 'pyboxes',
    'version': '1.0.1',
    'description': 'Pyboxes',
    'long_description': 'Pybox\n=====\n\n|PyPI| |Status| |Python Version| |License|\n\n|Read the Docs| |Tests| |Codecov|\n\n|pre-commit| |Black|\n\n.. |PyPI| image:: https://img.shields.io/pypi/v/pyboxes.svg\n   :target: https://pypi.org/project/pybox/\n   :alt: PyPI\n.. |Status| image:: https://img.shields.io/pypi/status/pyboxes.svg\n   :target: https://pypi.org/project/pybox/\n   :alt: Status\n.. |Python Version| image:: https://img.shields.io/pypi/pyversions/pyboxes\n   :target: https://pypi.org/project/pybox\n   :alt: Python Version\n.. |License| image:: https://img.shields.io/pypi/l/pyboxes\n   :target: https://opensource.org/licenses/MIT\n   :alt: License\n.. |Read the Docs| image:: https://img.shields.io/readthedocs/pyboxes/latest.svg?label=Read%20the%20Docs\n   :target: https://pybox.readthedocs.io/\n   :alt: Read the documentation at https://pyboxes.readthedocs.io/\n.. |Tests| image:: https://github.com/cauliyang/pybox/workflows/Tests/badge.svg\n   :target: https://github.com/cauliyang/pybox/actions?workflow=Tests\n   :alt: Tests\n.. |Codecov| image:: https://codecov.io/gh/cauliyang/pybox/branch/main/graph/badge.svg\n   :target: https://codecov.io/gh/cauliyang/pybox\n   :alt: Codecov\n.. |pre-commit| image:: https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white\n   :target: https://github.com/pre-commit/pre-commit\n   :alt: pre-commit\n.. |Black| image:: https://img.shields.io/badge/code%20style-black-000000.svg\n   :target: https://github.com/psf/black\n   :alt: Black\n\n\nAims\n--------\n\n- **Simple**:\n  - A simple and easy to use Python library for many annoy task.\n\n\nFeatures\n------------\n\n- `Google Driver`_:\n  - A simple and easy to download files by sharing link of Google Driver.\n\n- More to come...\n\nInstallation\n------------\n\nYou can install *Pybox* via pip_ from PyPI_:\n\n.. code:: console\n\n   $ pip install pybox\n\n\nUsage\n-----\n\nPlease see the `Command-line Reference <Usage_>`_ for details.\n\n\nContributing\n------------\n\nContributions are very welcome.\nTo learn more, see the `Contributor Guide`_.\n\n\nLicense\n-------\n\nDistributed under the terms of the `MIT license`_,\n*Pybox* is free and open source software.\n\n\nIssues\n------\n\nIf you encounter any problems,\nplease `file an issue`_ along with a detailed description.\n\n\nCredits\n-------\n\n.. _@cjolowicz: https://github.com/cjolowicz\n.. _Cookiecutter: https://github.com/audreyr/cookiecutter\n.. _MIT license: https://opensource.org/licenses/MIT\n.. _PyPI: https://pypi.org/\n.. _Hypermodern Python Cookiecutter: https://github.com/cjolowicz/cookiecutter-hypermodern-python\n.. _file an issue: https://github.com/cauliyang/pybox/issues\n.. _pip: https://pip.pypa.io/\n.. github-only\n.. _Contributor Guide: CONTRIBUTING.rst\n.. _Usage: https://pybox.readthedocs.io/en/latest/usage.html\n.. _Google Driver: https://www.google.com/drive/\n',
    'author': 'yangli',
    'author_email': 'li002252@umn.edu',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/cauliyang/pybox',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
