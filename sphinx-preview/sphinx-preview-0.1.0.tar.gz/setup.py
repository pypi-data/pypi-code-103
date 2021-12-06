# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['sphinx_preview']

package_data = \
{'': ['*'], 'sphinx_preview': ['assets/*']}

extras_require = \
{':extra == "docs"': ['sphinx>=4,<5']}

setup_kwargs = {
    'name': 'sphinx-preview',
    'version': '0.1.0',
    'description': '',
    'long_description': '.. image:: https://github.com/useblocks/sphinx-preview/raw/main/docs/_static/sphinx-preview-logo.png\n   :align: center\n   :width: 50%\n   :target: https://sphinx-preview.readthedocs.io/en/latest/\n   :alt: Sphinx-Preview\n\n\n`Sphinx <https://www.sphinx-doc.org>`_ extension to show previews for links, if a mouse hovers is detected.\n\nDocs\n----\n\nSee complete documentation under: https://sphinx-preview.readthedocs.io/en/latest/\n\nShowcase\n--------\n.. image:: https://github.com/useblocks/sphinx-preview/raw/main/docs/_static/sphinx-preview-showcase.gif\n   :align: center\n   :width: 100%\n\n\n\n\n',
    'author': 'team useblocks',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/useblocks/sphinx-preview',
    'packages': packages,
    'package_data': package_data,
    'extras_require': extras_require,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
