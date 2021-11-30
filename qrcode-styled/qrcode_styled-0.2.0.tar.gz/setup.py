# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['qrcode_styled',
 'qrcode_styled.base',
 'qrcode_styled.pil',
 'qrcode_styled.pil.figures',
 'qrcode_styled.svg',
 'qrcode_styled.svg.figures']

package_data = \
{'': ['*']}

install_requires = \
['Pillow>=8.4.0,<9.0.0', 'qrcode>=6.1,<7.0']

extras_require = \
{'svg': ['lxml>=4.6.4,<5.0.0']}

setup_kwargs = {
    'name': 'qrcode-styled',
    'version': '0.2.0',
    'description': 'Python port for kozakdenys/qr-code-styling',
    'long_description': '# Welcome\n\n[![PyPI version](https://badge.fury.io/py/qrcode-styled.svg)](https://badge.fury.io/py/qrcode-styled) [![codecov](https://codecov.io/gh/AdamBrianBright/qrcode_styled/branch/master/graph/badge.svg?token=MMDPS40REC)](https://codecov.io/gh/AdamBrianBright/qrcode_styled) [![FOSSA Status](https://app.fossa.com/api/projects/git%2Bgithub.com%2FAdamBrianBright%2Fqrcode_styled.svg?type=shield)](https://app.fossa.com/projects/git%2Bgithub.com%2FAdamBrianBright%2Fqrcode_styled?ref=badge_shield)\n\n## QRCode Styled [\\[WIP\\]](https://dictionary.cambridge.org/us/dictionary/english/wip?q=WIP)\n\n<img src="./img/logo.png" alt="QRCode Styled" width="64" height="64" />\n\nThis is a python port for a [browser QRCode generator](https://github.com/kozakdenys/qr-code-styling)\nby [Denys Kozak](https://github.com/kozakdenys)\n\nThis project was initially created for internal use in [cifrazia.com](https://cifrazia.com/).\n\nWe do not intend to maintain this project for wide usage, but feel free to use it, share, edit or submit pull requests.\n\n## Features\n\n+ Multiple formats:\n   + [x] SVG using `xmls`\n   + [x] PNG/WEBP, etc. using `Pillow`\n+ Multiple styles:\n   + [x] Extra rounded corners\n   + [ ] Rounded corners\n   + [ ] Straight\n   + [ ] Dotted\n\nCheck out [our documentation](https://adambrianbright.github.io/qrcode_styled/get-started/).\n\n## Installing\n\nUsing **Poetry**\n\n```shell\npoetry add qrcode-styled\n```\n\nUsing **PIP**\n\n```shell\npip install qrcode-styled\n```\n\n### Requirements\n\n+ Python `>= 3.9`\n+ Pillow `>= 8.2.0`\n+ qrcode `>= 6.1`\n+ lxml `>= 8.2.0` (optional, for SVG rendering)\n\n### Extras\n\n| Keyword | Description                | Packages        |\n| ------- | -------------------------- | --------------- |\n| `svg`   | Allows you to generate SVG | `lxml >= 4.6.3` |\n\n| SVG                           | WEBp                           |\n| ----------------------------- | ------------------------------ |\n| ![Svg QRCode](./img/test.svg) | ![Svg QRCode](./img/test.webp) |\n\n## Usage\n\n:::code source="./code/get-started.py" :::\n\n[![FOSSA Status](https://app.fossa.com/api/projects/git%2Bgithub.com%2FAdamBrianBright%2Fqrcode_styled.svg?type=large)](https://app.fossa.com/projects/git%2Bgithub.com%2FAdamBrianBright%2Fqrcode_styled?ref=badge_large)',
    'author': 'Bogdan Parfenov',
    'author_email': 'adam.brian.bright@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://cifrazia.com',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
