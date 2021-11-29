# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['stegano',
 'stegano.exifHeader',
 'stegano.lsb',
 'stegano.lsbset',
 'stegano.red',
 'stegano.steganalysis']

package_data = \
{'': ['*']}

install_requires = \
['crayons>=0.4.0,<0.5.0',
 'opencv-python>=4.5.0,<5.0.0',
 'piexif>=1.1.3,<2.0.0',
 'pillow>=8.2.0,<9.0.0']

entry_points = \
{'console_scripts': ['stegano-lsb = bin.lsb:main',
                     'stegano-lsb-set = bin.lsbset:main',
                     'stegano-red = bin.red:main',
                     'stegano-steganalysis-parity = bin.parity:main',
                     'stegano-steganalysis-statistics = bin.statistics:main']}

setup_kwargs = {
    'name': 'stegano',
    'version': '0.10.0',
    'description': 'A pure Python Steganography module.',
    'long_description': '# Stegano\n\n[![builds.sr.ht status](https://builds.sr.ht/~cedric/stegano.svg)](https://builds.sr.ht/~cedric/stegano)\n\n\n[Stegano](https://sr.ht/~cedric/stegano), a pure Python Steganography\nmodule.\n\nSteganography is the art and science of writing hidden messages in such a way\nthat no one, apart from the sender and intended recipient, suspects the\nexistence of the message, a form of security through obscurity. Consequently,\nfunctions provided by Stegano only hide messages, without encryption.\nSteganography is often used with cryptography.\n\nFor reporting issues, visit the tracker here:\nhttps://todo.sr.ht/~cedric/stegano\n\n\n## Installation\n\n\n```bash\n$ poetry install stegano\n```\n\nYou will be able to use Stegano in your Python programs.\n\nIf you only want to install Stegano as a command line tool:\n\n```bash\n$ pipx install stegano\n```\n\npipx installs scripts (system wide available) provided by Python packages into\nseparate virtualenvs to shield them from your system and each other.\n\n\n## Usage\n\nA [tutorial](https://stegano.readthedocs.io) is available.\n\n\n## Use Stegano as a library in your Python program\n\nIf you want to use Stegano in your Python program you just have to import the\nappropriate steganography technique. For example:\n\n```python\n>>> from stegano import lsb\n>>> secret = lsb.hide("./tests/sample-files/Lenna.png", "Hello World")\n>>> secret.save("./Lenna-secret.png")\n>>>\n>>> clear_message = lsb.reveal("./Lenna-secret.png")\n```\n\n\n## Use Stegano as a command line tool\n\n### Hide and reveal a message\n\n```bash\n$ stegano-lsb hide -i ./tests/sample-files/Lenna.png -m "Secret Message" -o Lena1.png\n$ stegano-lsb reveal -i Lena1.png\nSecret Message\n```\n\n\n### Hide the message with the Sieve of Eratosthenes\n\n```bash\n$ stegano-lsb-set hide -i ./tests/sample-files/Lenna.png -m \'Secret Message\' --generator eratosthenes -o Lena2.png\n```\n\nThe message will be scattered in the picture, following a set described by the\nSieve of Eratosthenes. Other sets are available. You can also use your own\ngenerators.\n\nThis will make a steganalysis more complicated.\n\n\n## Running the tests\n\n```bash\n$ python -m unittest discover -v\n```\n\nRunning the static type checker:\n\n```bash\n$ mypy stegano\n```\n\n\n## Contributions\n\nContributions are welcome. If you want to contribute to Stegano I highly\nrecommend you to install it in a Python virtual environment with poetry.\n\n\n## License\n\nThis software is licensed under\n[GNU General Public License version 3](https://www.gnu.org/licenses/gpl-3.0.html)\n\nCopyright (C) 2010-2021 [Cédric Bonhomme](https://www.cedricbonhomme.org)\n\nFor more information, [the list of authors and contributors](CONTRIBUTORS.md) is available.\n',
    'author': 'Cédric Bonhomme',
    'author_email': 'cedric@cedricbonhomme.org',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://sr.ht/~cedric/stegano',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
