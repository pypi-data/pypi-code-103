# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['mecha', 'mecha.contrib', 'mecha.contrib.scripting', 'mecha.resources']

package_data = \
{'': ['*']}

install_requires = \
['beet>=0.45.1', 'tokenstream>=1.2.6,<2.0.0']

entry_points = \
{'beet': ['commands = mecha.commands'],
 'console_scripts': ['mecha = mecha.cli:main']}

setup_kwargs = {
    'name': 'mecha',
    'version': '0.15.1',
    'description': 'A powerful Minecraft command library',
    'long_description': '<img align="right" src="https://raw.githubusercontent.com/mcbeet/mecha/main/logo.png" alt="logo" width="76">\n\n# Mecha\n\n[![GitHub Actions](https://github.com/mcbeet/mecha/workflows/CI/badge.svg)](https://github.com/mcbeet/mecha/actions)\n[![PyPI](https://img.shields.io/pypi/v/mecha.svg)](https://pypi.org/project/mecha/)\n[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/mecha.svg)](https://pypi.org/project/mecha/)\n[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)\n[![Discord](https://img.shields.io/discord/900530660677156924?color=7289DA&label=discord&logo=discord&logoColor=fff)](https://discord.gg/98MdSGMm8j)\n\n> A powerful Minecraft command library.\n\n```python\nfrom mecha import Mecha\n\nmc = Mecha()\n\nfunction = """\n    execute\n        as @a                        # For each "player",\n        at @s                        # start at their feet.\n        anchored eyes                # Looking through their eyes,\n        facing 0 0 0                 # face perfectly at the target\n        anchored feet                # (go back to the feet)\n        positioned ^ ^ ^1            # and move one block forward.\n        rotated as @s                # Face the direction the player\n                                     # is actually facing,\n        positioned ^ ^ ^-1           # and move one block back.\n        if entity @s[distance=..0.6] # Check if we\'re close to the\n                                     # player\'s feet.\n        run\n            say I\'m facing the target!\n"""\n\nast = mc.parse(function, multiline=True)\nprint(mc.serialize(ast))  # execute as @a at @s anchored eyes facing ...\n```\n\n## Introduction\n\nThis package provides everything you need for working with Minecraft commands in Python, whether you\'re looking to process commands or build abstractions on top.\n\n### Features\n\n- Extensible and version-agnostic `mcfunction` parser\n- Clean, immutable and hashable abstract syntax tree with source location\n- Command config resolver that flattens and enumerates all the valid command prototypes\n- Powerful rule dispatcher for processing specific ast nodes\n- Composable ast visitors and reducers\n- Comes with useful syntactic extensions like nesting and implicit execute\n- Execute arbitrary compilation passes in your [`beet`](https://github.com/mcbeet/beet) pipeline\n- _(soon)_ Expressive command API for writing commands in Python\n\n## Credits\n\n- [A few test cases are adapted from `SPYGlass`](https://github.com/SPYGlassMC/SPYGlass)\n- [Multiline example by `AjaxGb` (MCC discord)](https://discord.com/channels/154777837382008833/157097006500806656/539318174466703361)\n- [Multiline syntax derived from the `hangman` plugin](https://github.com/mcbeet/beet/blob/main/beet/contrib/hangman.py)\n- [Partially inspired by `Trident`](https://energyxxer.com/trident/)\n\n## Installation\n\nThe package can be installed with `pip`.\n\n```bash\n$ pip install mecha\n```\n\n## Command-line utility\n\n```bash\n$ mecha --help\nUsage: mecha [OPTIONS] [SOURCE]...\n\n  Validate data packs and .mcfunction files.\n\nOptions:\n  -m, --minecraft VERSION  Minecraft version.\n  -l, --log LEVEL          Configure output verbosity.\n  -v, --version            Show the version and exit.\n  -h, --help               Show this message and exit.\n```\n\nYou can use the command-line utility to check data packs and function files for errors. The command arguments can be zipped and unzipped data packs, individual function files, and if you specify a directory that\'s not a data pack it will recursively grab all the `.mcfunction` files in the directory. You can use the `--minecraft` option to select between versions `1.16`, `1.17`, and `1.18`.\n\n```bash\n$ mecha path/to/my_data_pack\nValidating with mecha v0.13.0\n\nERROR  | mecha  Expected curly \'}\' but got bracket \']\'.\n       | path/to/my_data_pack/data/demo/functions/foo.mcfunction:5:34\n       |      4 |\n       |      5 |  say hello @a[scores={foo=1, bar=2]\n       |        :                                   ^\n\nError: Reported 1 error.\n```\n\n## Github action\n\nYou can use `mecha` to check your data packs and function files for errors without having to install anything using the [`mcbeet/check-commands`](https://github.com/mcbeet/check-commands) github action.\n\n```yml\n# .github/workflows/check-commands.yml\nname: Check commands\non: [push]\n\njobs:\n  check:\n    runs-on: ubuntu-latest\n    steps:\n      - uses: actions/checkout@v2\n      - uses: mcbeet/check-commands@v1\n        with:\n          source: .\n```\n\nThis allows you to make sure that your commands don\'t contain any error when you push to your repository. For more details check out the [action README](https://github.com/mcbeet/check-commands#usage).\n\n## Contributing\n\nContributions are welcome. Make sure to first open an issue discussing the problem or the new feature before creating a pull request. The project uses [`poetry`](https://python-poetry.org/).\n\n```bash\n$ poetry install\n```\n\nYou can run the tests with `poetry run pytest`.\n\n```bash\n$ poetry run pytest\n```\n\nThe project must type-check with [`pyright`](https://github.com/microsoft/pyright). If you\'re using VSCode the [`pylance`](https://marketplace.visualstudio.com/items?itemName=ms-python.vscode-pylance) extension should report diagnostics automatically. You can also install the type-checker locally with `npm install` and run it from the command-line.\n\n```bash\n$ npm run watch\n$ npm run check\n```\n\nThe code follows the [`black`](https://github.com/psf/black) code style. Import statements are sorted with [`isort`](https://pycqa.github.io/isort/).\n\n```bash\n$ poetry run isort mecha tests\n$ poetry run black mecha tests\n$ poetry run black --check mecha tests\n```\n\n---\n\nLicense - [MIT](https://github.com/mcbeet/mecha/blob/main/LICENSE)\n',
    'author': 'Valentin Berlier',
    'author_email': 'berlier.v@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/mcbeet/mecha',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
