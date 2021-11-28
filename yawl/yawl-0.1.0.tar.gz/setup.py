# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['yawl', 'yawl.clients', 'yawl.shared', 'yawl.workflows']

package_data = \
{'': ['*']}

install_requires = \
['google-cloud-bigquery-datatransfer>=3.3.1,<4.0.0',
 'google-cloud-bigquery-storage==2.0.0',
 'google-cloud-bigquery>=2.6.0,<3.0.0',
 'pandas>=1.3.2,<2.0.0',
 'pytest-xdist>=2.3.0,<3.0.0']

setup_kwargs = {
    'name': 'yawl',
    'version': '0.1.0',
    'description': 'Yet Another WorkLoad - manage scheduled queries [currently] on BigQuery',
    'long_description': '# YAWL - Yet Another Workload\n[\n![Checks](https://img.shields.io/github/checks-status/gbieul/yawl/master)\n![Checks](https://github.com/gbieul/yawl/actions/workflows/yawl-checks.yml/badge.svg)\n![Build](https://github.com/gbieul/yawl/actions/workflows/yawl-build.yml/badge.svg)\n![License](https://img.shields.io/github/license/gbieul/flake8-markdown.svg)\n](https://pypi.org/project/flake8-markdown/)\n\n## 1.0. Intro\n\n## 2.0. Installing YAWL\n\n## 3.0. Using YAWL\n    ',
    'author': 'Gabriel Benvegmi',
    'author_email': 'gbieul_benveg@outlook.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/johnfraney/flake8-markdown',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7.1,<4.0',
}


setup(**setup_kwargs)
