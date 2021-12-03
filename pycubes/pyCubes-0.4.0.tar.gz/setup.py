# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['cubes', 'cubes.net', 'cubes.net.serializers', 'cubes.types_']

package_data = \
{'': ['*']}

install_requires = \
['anyio>=3.4.0,<4.0.0', 'nbtlib==2.0.4', 'pydantic>=1.8.2,<2.0.0']

extras_require = \
{'docs': ['mkdocs-material>=8.0.3,<9.0.0',
          'mkdocs-static-i18n>=0.22,<0.23',
          'pymdown-extensions>=9.1,<10.0']}

setup_kwargs = {
    'name': 'pycubes',
    'version': '0.4.0',
    'description': 'Library for creating servers and clients for Minecraft Java Edition',
    'long_description': '<h1 align="center">pyCubes</h1>\n\n<p align="center">\n<a href="https://pypi.org/project/pycubes"><img alt="PyPI" src="https://img.shields.io/pypi/v/pycubes"></a>\n<a href="https://pypi.org/project/pycubes"><img alt="PyPI - Python Version" src="https://img.shields.io/pypi/pyversions/pycubes"></a>\n<a href="https://pypi.org/project/pycubes"><img alt="PyPI - License" src="https://img.shields.io/pypi/l/pyCubes"></a>\n<a href="https://pepy.tech/project/pycubes"><img alt="Downloads" src="https://pepy.tech/badge/pycubes/month"></a>\n</p>\n<p align="center">\n<a href="https://github.com/DavisDmitry/pyCubes/actions/workflows/test.yml"><img alt="Test" src="https://github.com/DavisDmitry/pyCubes/actions/workflows/test.yml/badge.svg"></a>\n<a href="https://github.com/DavisDmitry/pyCubes/actions/workflows/lint.yml"><img alt="Lint" src="https://github.com/DavisDmitry/pyCubes/actions/workflows/lint.yml/badge.svg"></a>\n<a href="https://codecov.io/gh/DavisDmitry/pyCubes"><img alt="codecov" src="https://codecov.io/gh/DavisDmitry/pyCubes/branch/master/graph/badge.svg?token=Y18ZNYT4YS"></a>\n</p>\n<p align="center">\n<a href="https://github.com/psf/black"><img alt="Code style: black" src="https://img.shields.io/badge/code%20style-black-000000.svg"></a>\n<a href="https://pycqa.github.io/isort"><img alt="Imports: isort" src="https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&labelColor=ef8336"></a>\n</p>\n\n---\n<p align="center">\n<a href="https://pycubes.dmitrydavis.xyz">Documentation</a> | \n<a href="https://github.com/DavisDmitry/pyCubes/tree/master/examples">Examples</a> | \n<a href="https://wiki.vg/Protocol">Protocol Specification</a>\n</p>\n\n---\npyCubes is a library for creating servers and clients for Minecraft Java Edition (1.14+).\n\n**❗ 0.x versions are not stable. The library API is subject to change.**\n\n## Installation\n\n```bash\npip install pyCubes\n```\n\nWith `fast` extra (includes ujson and uvloop):\n\n```bash\npip install pyCubes[fast]\n```\n\n## Features\n\n* Serializers for [Data types](https://wiki.vg/Data_types) (missing Chat (use String instead), Shunk Section (1.18) and Palleted container (1.18))\n* Connection\n* Low level server\n* NBT module (wrapper over the [nbtlib](https://github.com/vberlier/nbtlib))\n* `generate_uuid` utility (generates UUID by player_name for using in offline mode)\n* [AnyIO](https://github.com/agronholm/anyio) support (an asynchronous networking and concurrency library)\n\n## TODO\n\n* [ ] Serializer for all packets Data types\n* [ ] Packets descriptor\n* [ ] Implement compression\n* [ ] High level server application with event driven API\n* [ ] High level client application with event driven API\n* [ ] High level proxy application with event driven API\n* [ ] Chat API (chat messages constructor)\n* [ ] Commands API\n* [ ] Add API Reference to docs\n',
    'author': 'Dmitry Davis',
    'author_email': 'dmitrydavis@protonmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/DavisDmitry/pyCubes',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
