# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['colorhash']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'colorhash',
    'version': '1.0.4',
    'description': 'Generate color based on any object',
    'long_description': '# color-hash\n\n**Generate a color based on a value**\n\nThis module generates a color based on an object, by calculating a color value\nbased on a hash value for the object. This means the result is deterministic:\nthe same value will always result in the same color (so long as the hash\nfunction remains deterministic).\n\nThis module is a port of the [color-hash Javascript library](https://github.com/zenozeng/color-hash). It supports\nPython 3.4+.\n\n## Quick Start\n\n```python\n>>> from colorhash import ColorHash\n>>> c = ColorHash(\'Hello World\')\n>>> c.hsl\n(131, 0.65, 0.5)\n>>> c.rgb\n(45, 210, 75)\n>>> c.hex\n\'#2dd24b\'\n```\n\n## Changelog\n\n- color-hash 1.0.4 *(2021-11-30)*\n  - Support only for python 3.6+\n  - Add tests\n- color-hash 1.0.3 *(2020-12-04)*\n  - Drop support for python 2\n  - Handover of project maintenance\n- color-hash 1.0.2 *(2016-07-08)*\n  - Add ``crc32_hash`` function and set default hashfunc to that. It\'s not\n    fully backwards-compatible, but I don\'t want to bump the version a lot for\n    not doing my research.\n- color-hash 1.0.0 *(2016-07-07)*\n  - Initial port.\n\n\n## License\n\nCopyright (c) 2016 Felix Krull <f_krull@gmx.de>\n\nThis is a port of the \'color-hash\' Javascript library which is:\n\nCopyright (c) 2015 Zeno Zeng\n\nPermission is hereby granted, free of charge, to any person obtaining a copy of\nthis software and associated documentation files (the "Software"), to deal in\nthe Software without restriction, including without limitation the rights to\nuse, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of\nthe Software, and to permit persons to whom the Software is furnished to do so,\nsubject to the following conditions:\n\nThe above copyright notice and this permission notice shall be included in all\ncopies or substantial portions of the Software.\n\nTHE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR\nIMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS\nFOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR\nCOPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER\nIN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN\nCONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.\n',
    'author': 'dimostenis',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/dimostenis/color-hash-python',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
