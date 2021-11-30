# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['sphinx_data_viewer']

package_data = \
{'': ['*'], 'sphinx_data_viewer': ['assets/*']}

extras_require = \
{':extra == "docs"': ['sphinx>=4,<5']}

setup_kwargs = {
    'name': 'sphinx-data-viewer',
    'version': '0.1.1',
    'description': 'Sphinx extension to show dta in an interacitve list view',
    'long_description': 'Sphinx-Data-Viewer\n==================\nAdds an interactive data viewer for data objects to Sphinx.\n\nUse it to document:\n\n* JSON data\n* JSON files\n* Python objects\n\n**Complete documentation and examples:** https://sphinx-data-viewer.readthedocs.io/en/latest/\n\n.. image:: https://github.com/useblocks/sphinx-data-viewer/raw/main/docs/_static/sphinx-data-viewer-intro.png\n   :width: 70%\n   :target: https://sphinx-data-viewer.readthedocs.io/en/latest/\n\nThe Javascript part is based on the wonderful work of https://github.com/pgrabovets/json-view.\n',
    'author': 'team useblocks',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/useblocks/sphinx-data-viewer',
    'packages': packages,
    'package_data': package_data,
    'extras_require': extras_require,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
