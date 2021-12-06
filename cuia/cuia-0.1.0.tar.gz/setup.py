# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['cuia', 'cuia.messages', 'cuia.renderer']

package_data = \
{'': ['*']}

install_requires = \
['cusser>=0.1.0,<0.2.0']

setup_kwargs = {
    'name': 'cuia',
    'version': '0.1.0',
    'description': '🧉🌿 A delightful tiny framework for building reliable text-based applications',
    'long_description': '[![PyPI](https://img.shields.io/pypi/v/cuia)](https://pypi.org/project/cuia/)\n[![Python package](https://github.com/getcuia/cuia/actions/workflows/python-package.yml/badge.svg)](https://github.com/getcuia/cuia/actions/workflows/python-package.yml)\n[![PyPI - License](https://img.shields.io/pypi/l/cuia)](https://github.com/getcuia/cuia/blob/main/LICENSE)\n\n# [cuia](https://github.com/getcuia/cuia#readme) 🧉\n\n<div align="center">\n    <img class="hero" src="https://github.com/getcuia/cuia/raw/main/banner.svg" alt="cuia" width="33%" />\n</div>\n\n> A delightful tiny framework for building reliable text-based applications.\n\n**cuia** is a tiny Python library for building interactive terminal user\ninterfaces that are easy to use, fast and have a small memory footprint.\n\ncuia is inspired by [Bubble Tea](https://github.com/charmbracelet/bubbletea) (written in [Go](https://golang.org/)) and, in particular, employs [the Elm architecture](https://guide.elm-lang.org/architecture/) (TEA, named after the [Elm programming language](https://elm-lang.org/)). This means that **cuia applications are as dynamic and easy to write (and use) as they could be**.\n\n## Features\n\n-   🧵 Simple: your user interface is a string of characters\n-   💬 Interaction-focused\n-   ♻️ Easily integrate with other libraries\n-   🕹️ Use the same escape code sequences\n    [as you would with Colorama](https://github.com/tartley/colorama#recognised-ansi-sequences)\n-   🖥️ Support for Unix variants out of the box:\n    [curses](https://docs.python.org/3/library/curses.html) under the hood by\n    default (and probably works on Windows and DOS if a compatible curses\n    library is available)\n-   🤬 Only one dependency: [cusser](https://github.com/getcuia/cusser) (for\n    wrapping the curses library)\n-   🐍 Python 3.8+\n\n## Installation\n\n```console\n$ pip install cuia\n```\n\n## Usage\n\n```python\nIn [1]: import asyncio\n\nIn [2]: from dataclasses import dataclass\n\nIn [3]: from cuia import Program, Store\n\nIn [4]: @dataclass\n   ...: class Hello(Store):\n   ...:\n   ...:     x: int = 0\n   ...:     y: int = 0\n   ...:\n   ...:     def __str__(self):\n   ...:         return f"\\033[{self.x};{self.y}H\\033[1mHello, 🌍!"\n   ...:\n\nIn [5]: program = Program(Hello(34, 12))\n\nIn [6]: asyncio.run(program.start())\n\n```\n\n![Screenshot](https://github.com/getcuia/cuia/raw/main/screenshot.png)\n\n## How does it work\n\ncuia is inspired by [Bubble Tea](https://github.com/charmbracelet/bubbletea)\n(written in [Go](https://golang.org/)) and, on the surface, looks much like it.\nIn particular, cuia employs\n[the Elm architecture](https://guide.elm-lang.org/architecture/) (TEA, named\nafter the [Elm programming language](https://elm-lang.org/)). What it means in\nterms of output is that a cuia application creates a new screen representation\nof the user interface (in fact, as a regular\n[Python string](https://docs.python.org/3/library/stdtypes.html#text-sequence-type-str))\nat each step. It might look as a serious memory overhead but, in fact, it will\nnever use more than 100kb to hold those string representations, even on large\nscreens[^how-big].\n\nBut, contrary to Bubble Tea, cuia is built on top of\n[curses](https://docs.python.org/3/library/curses.html). curses is a standard\nPython library (written in\n[C](<https://en.wikipedia.org/wiki/C_(programming_language)>)) that wraps the\nfamous [ncurses](https://en.wikipedia.org/wiki/Ncurses) library (written in C as\nwell). ncurses does\n[efficient screen updates](https://invisible-island.net/ncurses/hackguide.html#output)\nand is thus quite fast. It works by comparing the contents of a screen buffer to\nthe contents of the actual screen and only updating where the contents have\nchanged. So, in general, cuia works in a similar way to\n[virtual DOM](https://en.wikipedia.org/wiki/Virtual_DOM) tree updates (a\ntechnique commonly used in\n[JavaScript web frameworks](https://en.wikipedia.org/wiki/Comparison_of_JavaScript-based_web_frameworks)\nsuch as [React](https://reactjs.org/)), except that it is a string buffer that\nis updated, instead of a virtual DOM tree.\n\n[^how-big]:\n    My 22" desktop can\'t make a terminal larger than 211x55 characters. A single\n    string representation would require a little over 10kb of storage in Python.\n    It would then take **ten** string representations to be hold in memory at a\n    single point in time for it to go beyond 100kb.\n',
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
