# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['sphinx_needs_enterprise',
 'sphinx_needs_enterprise.extensions',
 'sphinx_needs_enterprise.scripts',
 'sphinx_needs_enterprise.services']

package_data = \
{'': ['*'], 'sphinx_needs_enterprise': ['templates/*']}

install_requires = \
['azure-devops>=6.0.0-beta.4',
 'click>=7.0',
 'elasticsearch>7.15',
 'jinja2>=2',
 'jira2markdown>=0.1',
 'licensing>=0.31',
 'm2r>=0.2',
 'requests>=2',
 'sphinxcontrib-needs>=0.7.2',
 'sphinxcontrib-programoutput>=0.17',
 'tqdm==4.62']

entry_points = \
{'console_scripts': ['sne = sphinx_needs_enterprise.scripts.cli:cli']}

setup_kwargs = {
    'name': 'sphinx-needs-enterprise',
    'version': '0.1.2',
    'description': '',
    'long_description': 'Sphinx-Needs Enterprise\n=======================\n\n.. image:: docs/_static/sphinx-needs-enterprise-logo.png\n   :align: center\n   :width: 41%\n\n``Sphinx-Needs Enterprise`` is a collection of additional functions for ``Sphinx-Needs``, which are useful mostly\nin company-based environments.\n\nThis repository contains the complete source code and documentation.\n\nLicense\n-------\nThis package is released under the Business Source License, which allows free usage for private projects and sets\nsome duties for commercial projects. For details please take a look into our\n`LICENSE <https://raw.githubusercontent.com/useblocks/sphinx-needs-enterprise/main/LICENSE>`_ file.\n\n|\n| **To use Sphinx-Needs-Enterprise in commercial projects a commercial license is needed.**\n| Please get it contact with `useblocks <https://useblocks.com>`_ or visit sphinx-needs.com.\n',
    'author': 'team useblocks',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'http://github.com/useblocks/sphinx-needs-enterprise',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
