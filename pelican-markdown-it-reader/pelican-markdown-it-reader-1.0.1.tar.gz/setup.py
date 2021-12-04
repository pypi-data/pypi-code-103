# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pelican', 'pelican.plugins.markdown_it_reader']

package_data = \
{'': ['*']}

install_requires = \
['Pygments>=2.6,<3.0',
 'markdown-it-py>=1.1,<3.0',
 'mdit-py-plugins>=0.2.8,<0.4.0',
 'pelican>=4.5,<5.0']

extras_require = \
{'markdown': ['markdown>=3.2.2,<4.0.0']}

setup_kwargs = {
    'name': 'pelican-markdown-it-reader',
    'version': '1.0.1',
    'description': 'Reader plugin for Markdown-IT-py replacement',
    'long_description': "Markdown-IT reader: A Plugin for Pelican\n====================================================\n\n[![Build Status](https://img.shields.io/github/workflow/status/gaige/markdown-it-reader/build)](https://github.com/gaige/markdown-it-reader/actions)\n[![PyPI Version](https://img.shields.io/pypi/v/pelican-markdown-it-reader)](https://pypi.org/project/pelican-markdown-it-reader/)\n![License](https://img.shields.io/pypi/l/pelican-markdown-it-reader?color=blue)\n\nReader plugin for Markdown-IT-py replacement\n\nThis is double-opinionated, in that it's opinionated using Markdown-IT\nand again because we add in some additions; in particular:\n\n- Tables\n- footnotes\n- Pygment-based syntax highlighting\n\nInstallation\n------------\n\nThis plugin can be installed via:\n\n    python -m pip install pelican-markdown-it-reader\n\n\nUsage\n-----\n\nThere are currently no configuration items.\n\nOnce installed it takes over responsibility for reading the following file extensions:\n\n - `md`\n - `markdown`\n - `mkd`\n - `mdown`\n\nBy taking over `link_open` and `image` render rules, the plugin handles replacing the\npelican link placeholders with appropriate `href` items which are then rendered to html.\n\nContributing\n------------\n\nContributions are welcome and much appreciated. Every little bit helps.\nYou can contribute by improving the documentation, adding missing features,\nand fixing bugs. You can also help out by reviewing and commenting on [existing issues][].\n\nTo start contributing to this plugin, review the [Contributing to Pelican][] documentation, beginning with the **Contributing Code** section.\n\n[existing issues]: https://github.com/gaige/markdown-it-reader/issues\n[Contributing to Pelican]: https://docs.getpelican.com/en/latest/contribute.html\n\nLicense\n-------\n\nThis project is licensed under the MIT license.\n",
    'author': 'Gaige B. Paulsen',
    'author_email': 'gaige@cluetrust.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/gaige/markdown-it-reader',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
