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
    'version': '0.2.6',
    'description': 'This software take a License and agregate into the project.',
    'long_description': '[![GitHub Actions (Tests)](https://github.com/incolumepy/incolumepy.makefilelicense/workflows/Tests/badge.svg)](https://github.com/incolumepy/incolumepy.makefilelicense/)\n[![codecov](https://codecov.io/gh/incolumepy/incolumepy.makefilelicense/branch/main/graph/badge.svg?token=QFULL7R8HX)](https://codecov.io/gh/incolumepy/incolumepy.makefilelicense)\n# Makefile License Incolume Python\n\n---\nThis software take a License (https://choosealicense.com/licenses/) and agregate into the project.\n\n## pip Install\n```bash\npip install incolumepy.makefilelicense\n```\n## poetry Install\n```bash\npoetry add incolumepy.makefilelicense\n```\n## source\n1. Choice the source on https://github.com/incolumepy/incolumepy.makefilelicense/tags;\n2. unzip your package;\n3. cd incolumepy.makefilelicense-x.y.z;\n4.\n\n## Command make\n```bash\nmake setup\nmake [license-agpl license-apache license-bsl license-cc0 license-gpl \\\n      license-lgpl license-mit license-mpl]\nmake test\n```\n',
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
    'python_requires': '>=3.6.14,<4.0.0',
}


setup(**setup_kwargs)
