# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': '.'}

packages = \
['makefilelicense', 'makefilelicense.exceptions']

package_data = \
{'': ['*'], 'makefilelicense': ['licenses/*']}

extras_require = \
{':python_version < "3.8"': ['importlib-metadata'],
 ':python_version >= "3.6" and python_version < "4.0"': ['toml[tomli]>=0.10.2,<0.11.0']}

entry_points = \
{'console_scripts': ['license-agpl = '
                     'incolumepy.makefilelicense.licenses:license_agpl',
                     'license-apache = '
                     'incolumepy.makefilelicense.licenses:license_apache',
                     'license-bsl = '
                     'incolumepy.makefilelicense.licenses:license_bsl',
                     'license-cc0 = '
                     'incolumepy.makefilelicense.licenses:license_cc0',
                     'license-gpl = '
                     'incolumepy.makefilelicense.licenses:license_gpl',
                     'license-lgpl = '
                     'incolumepy.makefilelicense.licenses:license_lgpl',
                     'license-mit = '
                     'incolumepy.makefilelicense.licenses:license_mit',
                     'license-mpl = '
                     'incolumepy.makefilelicense.licenses:license_mpl',
                     'license-ul = '
                     'incolumepy.makefilelicense.licenses:unlicense',
                     'unlicense = '
                     'incolumepy.makefilelicense.licenses:unlicense']}

setup_kwargs = {
    'name': 'incolumepy.makefilelicense',
    'version': '0.2.10',
    'description': 'This software take a License and agregate into the project.',
    'long_description': '![PyPI - Python Version](https://img.shields.io/pypi/pyversions/incolumepy.makefilelicense)\n![PyPI - Status](https://img.shields.io/pypi/status/incolumepy.makefilelicense)\n[![GitHub Actions (Tests)](https://github.com/incolumepy/incolumepy.makefilelicense/workflows/Tests/badge.svg)](https://github.com/incolumepy/incolumepy.makefilelicense/)\n[![codecov](https://codecov.io/gh/incolumepy/incolumepy.makefilelicense/branch/main/graph/badge.svg?token=QFULL7R8HX)](https://codecov.io/gh/incolumepy/incolumepy.makefilelicense)\n![PyPI](https://img.shields.io/pypi/v/incolumepy.makefilelicense)\n![GitHub tag (latest by date)](https://img.shields.io/github/v/tag/incolumepy/incolumepy.makefilelicense?logo=tag)\n![PyPI - Wheel](https://img.shields.io/pypi/wheel/incolumepy.makefilelicense)\n![PyPI - Implementation](https://img.shields.io/pypi/implementation/incolumepy.makefilelicense)\n![PyPI - License](https://img.shields.io/pypi/l/incolumepy.makefilelicense)\n!["Code style: black"](https://img.shields.io/badge/code%20style-black-black)\n![GitHub code size in bytes](https://img.shields.io/github/languages/code-size/incolumepy/incolumepy.makefilelicense)\n![GitHub repo size](https://img.shields.io/github/repo-size/incolumepy/incolumepy.makefilelicense)\n![GitHub issues](https://img.shields.io/github/issues/incolumepy/incolumepy.makefilelicense)\n![GitHub closed issues](https://img.shields.io/github/issues-closed/incolumepy/incolumepy.makefilelicense)\n![GitHub closed issues by-label](https://img.shields.io/github/issues-closed/incolumepy/incolumepy.makefilelicense/enhancement)\n![GitHub issues by-label](https://img.shields.io/github/issues/incolumepy/incolumepy.makefilelicense/bug)\n![GitHub issues by-label](https://img.shields.io/github/issues/incolumepy/incolumepy.makefilelicense/enhancement)\n[![Downloads](https://pepy.tech/badge/incolumepy-makefilelicense)](https://pepy.tech/project/incolumepy-makefilelicense)\n[![Downloads](https://pepy.tech/badge/incolumepy-makefilelicense/month)](https://pepy.tech/project/incolumepy-makefilelicense)\n[![Downloads](https://pepy.tech/badge/incolumepy-makefilelicense/week)](https://pepy.tech/project/incolumepy-makefilelicense)\n# Makefile License Incolume Python\n\n---\nThis software take a License (https://choosealicense.com/licenses/) and agregate into the project.\n\n## pip Install\n```bash\npip install incolumepy.makefilelicense\n```\n## poetry Install\n```bash\npoetry add incolumepy.makefilelicense\n```\n\n[//]: # (## source)\n[//]: # (1. Choice the source on https://github.com/incolumepy/incolumepy.makefilelicense/tags;)\n[//]: # (2. unzip your package;)\n[//]: # (3. cd incolumepy.makefilelicense-x.y.z;)\n[//]: # (4.)\n\n## Command make\nLicenses avaliables:\n```bash\nmake [license-agpl license-apache license-bsl license-cc0 license-gpl \\\n      license-lgpl license-mit license-mpl]\n```\n\nOptions for make command:\n```bash\n$ make\nclean                help                 license-boost-v1\nlicense-gnu-gpl-v3   license-mozilla-v2   release\ntox                  clean-all            install\nlicense-cc0          license-gnu-lgpl-v3  lint\nsetup                unlicense            format\nlicense-apache-v2    license-gnu-agpl-v3  license-mit\nprerelease           test\n```\n',
    'author': 'Britodfbr',
    'author_email': 'britodfbr@gmail.com',
    'maintainer': 'Britodfbr',
    'maintainer_email': 'britodfbr@gmail.com',
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.6.8,<4.0.0',
}


setup(**setup_kwargs)
