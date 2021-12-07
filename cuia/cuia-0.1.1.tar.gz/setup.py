# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['cuia', 'cuia.messages', 'cuia.renderer']

package_data = \
{'': ['*']}

install_requires = \
['cusser>=0.1.1,<0.2.0']

setup_kwargs = {
    'name': 'cuia',
    'version': '0.1.1',
    'description': '🧉🌿 A delightful tiny framework for building reliable text-based applications',
    'long_description': '[![PyPI](https://img.shields.io/pypi/v/cuia)](https://pypi.org/project/cuia/)\n[![Python package](https://github.com/getcuia/cuia/actions/workflows/python-package.yml/badge.svg)](https://github.com/getcuia/cuia/actions/workflows/python-package.yml)\n[![PyPI - License](https://img.shields.io/pypi/l/cuia)](https://github.com/getcuia/cuia/blob/main/LICENSE)\n\n# [cuia](https://github.com/getcuia/cuia#readme) 🧉\n\n<div align="center">\n    <img class="hero" src="https://github.com/getcuia/cuia/raw/main/banner.svg" alt="cuia" width="33%" />\n</div>\n\n> A delightful tiny framework for building reliable text-based applications.\n\n**cuia** is a tiny Python library for building interactive terminal user\ninterfaces that are easy to use, fast and have a small memory footprint.\n\ncuia is inspired by [Bubble Tea](https://github.com/charmbracelet/bubbletea)\n(written in [Go](https://golang.org/)) and, in particular, employs\n[the Elm architecture](https://guide.elm-lang.org/architecture/) (TEA, named\nafter the [Elm programming language](https://elm-lang.org/)). This means that\n**cuia applications are as dynamic and easy to write (and use) as they could\nbe**.\n\n## Features\n\n-   🧵 Simple: your user interface is a string of characters\n-   💬 Interaction-focused\n-   ♻️ Easily integrate with other libraries\n-   🕹️ Use the same escape code sequences\n    [as you would with Colorama](https://github.com/tartley/colorama#recognised-ansi-sequences)\n-   🖥️ Support for Unix variants out of the box:\n    [curses](https://docs.python.org/3/library/curses.html) under the hood by\n    default (and probably works on Windows and DOS if a compatible curses\n    library is available)\n-   🤬 Only one dependency: [cusser](https://github.com/getcuia/cusser) (for\n    wrapping the curses library)\n-   🐍 Python 3.8+\n\n## Installation\n\n```console\n$ pip install cuia\n```\n\n## Usage\n\n```python\nIn [1]: import asyncio\n\nIn [2]: from dataclasses import dataclass\n\nIn [3]: from cuia import Program, Store\n\nIn [4]: @dataclass\n   ...: class Hello(Store):\n   ...:\n   ...:     x: int = 0\n   ...:     y: int = 0\n   ...:\n   ...:     def __str__(self):\n   ...:         return f"\\033[{self.x};{self.y}H\\033[1mHello, 🌍!"\n   ...:\n\nIn [5]: program = Program(Hello(34, 12))\n\nIn [6]: asyncio.run(program.start())\n\n```\n\n![Screenshot](https://github.com/getcuia/cuia/raw/main/screenshot.png)\n',
    'author': 'Felipe S. S. Schneider',
    'author_email': 'schneider.felipe@posgrad.ufsc.br',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/getcuia/cuia',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
