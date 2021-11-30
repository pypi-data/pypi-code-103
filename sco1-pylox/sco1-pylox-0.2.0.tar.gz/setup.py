# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pylox', 'pylox.containers', 'pylox.protocols', 'tool']

package_data = \
{'': ['*']}

install_requires = \
['attrs>=21.2,<22.0', 'rich>=10.12,<11.0', 'typer>=0.4,<0.5']

entry_points = \
{'console_scripts': ['astgen = tool.generate_ast:astgen_cli',
                     'pylox = pylox.lox:pylox_cli',
                     'testgen = tool.generate_tests:testgen_cli']}

setup_kwargs = {
    'name': 'sco1-pylox',
    'version': '0.2.0',
    'description': 'A Python interpreter for the Lox programming language.',
    'long_description': '# pylox\n[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/sco1-pylox)](https://pypi.org/project/sco1-pylox/)\n[![PyPI - Version](https://img.shields.io/pypi/v/sco1-pylox)](https://pypi.org/project/sco1-pylox/)\n[![PyPI - License](https://img.shields.io/pypi/l/sco1-pylox?color=magenta)](https://github.com/sco1/sco1-pylox/blob/main/LICENSE)\n[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/sco1/pylox/main.svg)](https://results.pre-commit.ci/latest/github/sco1/pylox/main)\n[![Code style: black](https://img.shields.io/badge/code%20style-black-black)](https://github.com/psf/black)\n[![Open in Visual Studio Code](https://open.vscode.dev/badges/open-in-vscode.svg)](https://open.vscode.dev/sco1/pylox)\n\n## Introduction\nThis is my Python implementation of an interpreter for the Lox programming language from Robert Nystrom\'s *[Crafting Interpreters](https://craftinginterpreters.com/)*.\n\n## Python?\nWhile the text is implemented in Java and C as its high & low-level implementations, I have no idea how to write either of them! Instead, I\'ll be using Python for the high-level implementation & eventually Rust for the low-level imeplementation.\n\n## Differences From Text\nFor the sake of fitting within a decently sized text, the fully implemented Lox spec omits features that users of other programming languages may miss. Often these are discussed as notes within a chapter, or presented as challenges at the end of a chapter. Significant difference in this implementation from the text reference are noted below.\n### Defined by Challenges\n  * (Chapter 4): Arbitrarily nested block comments (`/* ... */`)\n  * (Chapter 9): `break` statements are available for `for` and `while` loops\n### User Choice\n  * Division by zero returns `NaN` (Python\'s `float(\'nan\')`)\n  * Strings may be defined using either `"` or `\'`\n  * Modulo operator (`%`)\n  * Power operator (`^`)\n  * Integer division operator (`\\`)\n  * Both floats and integers are represented\n    * Return type from operations follows Python3\'s semantics\n  * Containers\n    * `array()`\n\n### Additional Built-ins:\nUnless otherwise noted, behavior mirrors the similarly named Python function\n  * `abs`\n  * `ceil`\n  * `divmod`\n  * `floor`\n  * `input`\n  * `len`\n  * `max`\n  * `mean`\n  * `median`\n  * `min`\n  * `mode`\n  * `ord`\n  * `read_text` (via `pathlib.Path.read_text`)\n  * `std`\n  * `string_array`\n    * Gives a `LoxArray` whose contents are equivalent to `collections.deque(<some string>)`\n',
    'author': 'sco1',
    'author_email': 'sco1.git@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/sco1/',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
