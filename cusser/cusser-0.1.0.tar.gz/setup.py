# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['cusser']

package_data = \
{'': ['*']}

install_requires = \
['stransi>=0.1.0,<0.2.0']

setup_kwargs = {
    'name': 'cusser',
    'version': '0.1.0',
    'description': 'A curses wrapper that understands ANSI escape code sequences',
    'long_description': '[![PyPI](https://img.shields.io/pypi/v/cusser)](https://pypi.org/project/cusser/)\n[![Python package](https://github.com/getcuia/cusser/actions/workflows/python-package.yml/badge.svg)](https://github.com/getcuia/cusser/actions/workflows/python-package.yml)\n[![PyPI - License](https://img.shields.io/pypi/l/cusser)](https://github.com/getcuia/cusser/blob/main/LICENSE)\n\n# [cusser](https://github.com/getcuia/cusser#readme) 🤬\n\n<div align="center">\n    <img class="hero" src="https://github.com/getcuia/cusser/raw/main/banner.jpg" alt="cusser" width="33%" />\n</div>\n\n> A curses wrapper that understands ANSI escape code sequences\n\ncusser is a lightweight Python package for teaching\n[curses](https://docs.python.org/3/library/curses.html) how to use\n[ANSI escape code sequences](https://en.wikipedia.org/wiki/ANSI_escape_code). It\nworks by wrapping the curses standard window object and intercepting escape code\nsequences.\n\n## Features\n\n-   ♻️ Easily integrate with the\n    [standard `curses` module](https://docs.python.org/3/library/curses.html)\n-   🖍️ Only one dependency: [stransi](https://github.com/getcuia/stransi) (for\n    actuallly parsing escape code sequences)\n-   🐍 Python 3.8+\n\n## Installation\n\n```console\n$ pip install cusser\n```\n\n## Usage\n\n```python\nIn [1]: import curses\n\nIn [2]: from cusser import Cusser\n\nIn [3]: def app(stdscr) -> None:\n   ...:     """Start a new application."""\n   ...:     if not isinstance(stdscr, Cusser):\n   ...:         stdscr = Cusser(stdscr)\n   ...:\n   ...:     ultra_violet = (100, 83, 148)\n   ...:     x, y = 34, 12\n   ...:     stdscr.addstr(\n   ...:         f"\\033[2J\\033[{x};{y}H"\n   ...:         "\\033[1;32mHello "\n   ...:         f"\\033[22;38;2;{\';\'.join(map(str, ultra_violet))}m"\n   ...:         "cusser"\n   ...:         "\\033[0m 🤬!"\n   ...:     )\n   ...:     stdscr.refresh()\n   ...:     stdscr.getch()\n   ...:\n\nIn [4]: curses.wrapper(app)\n```\n\n![Screenshot](https://github.com/getcuia/cusser/raw/main/screenshot.png)\n\n## Credits\n\n[Photo](https://github.com/getcuia/cusser/raw/main/banner.jpg) by\n[Gwendal Cottin](https://unsplash.com/@gwendal?utm_source=unsplash&utm_medium=referral&utm_content=creditCopyText)\non\n[Unsplash](https://unsplash.com/?utm_source=unsplash&utm_medium=referral&utm_content=creditCopyText).\n',
    'author': 'Felipe S. S. Schneider',
    'author_email': 'schneider.felipe@posgrad.ufsc.br',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/getcuia/cusser',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
