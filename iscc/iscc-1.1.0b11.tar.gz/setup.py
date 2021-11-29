# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['iscc']

package_data = \
{'': ['*']}

install_requires = \
['annoy>=1.17,<2.0',
 'av>=8.0.3,<9.0.0',
 'bidict>=0.21,<0.22',
 'codetiming>=1.3,<2.0',
 'humanize>=3.12,<4.0',
 'iscc-core>=0.1,<0.2',
 'jmespath>=0.10,<0.11',
 'langcodes>=3.3,<4.0',
 'langdetect>=1.0.9,<2.0.0',
 'lmdb>=1.2,<2.0',
 'loguru<0.6',
 'mobi>=0.3,<0.4',
 'msgpack>=1.0,<2.0',
 'numpy==1.19.3',
 'pyexiv2==2.7.1',
 'python-dotenv>=0.19,<0.20',
 'requests>=2.26,<3.0',
 'tika>=1.24,<2.0']

extras_require = \
{':sys_platform == "linux"': ['python-magic>=0.4.22,<0.5.0'],
 ':sys_platform == "win32" or sys_platform == "darwin"': ['python-magic-bin>=0.4.14,<0.5.0'],
 'optional': ['scenedetect>=0.5.5,<0.6.0',
              'opencv-contrib-python-headless>=4.5,<5.0']}

setup_kwargs = {
    'name': 'iscc',
    'version': '1.1.0b11',
    'description': 'ISCC: Reference Implementation',
    'long_description': '# ISCC - Spec and Reference Code\n\n[![Build](https://github.com/iscc/iscc-specs/actions/workflows/test.yml/badge.svg?branch=version-1.1)](https://github.com/iscc/iscc-specs/actions/workflows/test.yml)\n[![License](https://img.shields.io/pypi/l/iscc.svg)](https://pypi.python.org/pypi/iscc/)\n[![Downloads](https://pepy.tech/badge/iscc)](https://pepy.tech/project/iscc)\n[![DOI](https://zenodo.org/badge/96668860.svg)](https://zenodo.org/badge/latestdoi/96668860)\n\nThe **International Standard Content Code** is a proposal for an [open standard](https://en.wikipedia.org/wiki/Open_standard) for decentralized content identification. This repository contains the specification of the proposed **ISCC Standard** and a reference implementation in Python3. The latest published version of the specification can be found at [iscc.codes](https://iscc.codes)\n\n| NOTE: This is ISCC Version 1.1 work in progress!!! |\n| --- |\n\n## Installing the reference code\n\nThe reference code is published with the package name [iscc](https://pypi.python.org/pypi/iscc) on Python Package Index. Install it with:\n\n``` bash\npip install iscc==1.1.0b10\n```\n\nIf your system is setup to compile c-extensions install with:\n\n``` bash\npip install iscc[turbo]==1.1.0b10\n```\n\nThis will install cython and build binary extansions for faster ISCC processing.\n\nTo install the required binaries for content extraction do:\n\n```python\nfrom iscc.bin import install\ninstall()\n```\n\n## Using the reference code\n\nA short example on how to create an ISCC Code with the reference implementation.\n\n``` python\n>>> import iscc\n>>> iscc.code_iscc("README.md", all_granular=True)\n{\'version\': \'0-0-0\',\n \'iscc\': \'KADYHLZUJ43U3LX7G7PNLS54JHAET3ANW4EQ3YQIP3LDAZHEYIS5GWI\',\n \'title\': \'# ISCC Spec and Reference Code\',\n \'filename\': \'README.md\',\n \'filesize\': 3840,\n \'mediatype\': \'text/markdown\',\n \'tophash\': \'00194e2c4e5570e637bd18667740fdcf7f1683d6ccace7f5c0cc6531f6e982e5\',\n \'metahash\': \'828dd01bf76b78fc448f6d2ab25008835d2993c6acde205235dc942083c4677d\',\n \'datahash\': \'d63064e4c225d3594bdf60c30bcb04554e53059d9077a6f330f8295b4420ded5\',\n \'gmt\': <GMT.text: \'text\'>,\n \'characters\': 3457,\n \'language\': \'en\',\n \'features\': [{\'kind\': <FeatureType.data: \'data\'>,\n               \'version\': 0,\n               \'features\': [\'7A23CQ3iCH4\'],\n               \'sizes\': [3840]},\n              {\'kind\': <FeatureType.text: \'text\'>,\n               \'version\': 0,\n               \'features\': [\'Nt6V67hJxmk\',\n                            \'9HvPYqt1rQw\',\n                            \'ld1FLbp7A50\',\n                            \'M8aTn6atuB0\'],\n               \'sizes\': [2340, 309, 292, 516]}]}\n```\n\n## Working with the specification\n\n| NOTE: This is ISCC Version 1.1 - The specs are not yet updated!!! |\n| --- |\n\nThe entire **ISCC Specification** is written in plain text [Markdown](https://en.wikipedia.org/wiki/Markdown). The markdown content is than built and published with the excellent [mkdocs](http://www.mkdocs.org/) documetation tool. If you have some basic command line skills you can build and run the specification site on your own computer. Make sure you have the [git](https://git-scm.com/) and [Python](https://www.python.org/) and [Poetry](https://pypi.org/project/poetry/) installed on your system and follow these steps on the command line:\n\n``` bash\ngit clone https://github.com/iscc/iscc-specs.git\ncd iscc-specs\npoetry install\nmkdocs serve\n```\n\nAll specification documents can be found in the `./docs` subfolder or the repository. The recommended editor for the markdown files is [Typora](https://typora.io/). If you have commit rights to the [main repository](https://github.com/iscc/iscc-specs) you can deploy the site with a simple `mkdocs gh-deploy`.\n\n## Contribute\n\nPull requests and other contributions are welcome. Use the [Github Issues](https://github.com/iscc/iscc-specs/issues) section of this project to discuss ideas for the **ISCC Specification**. You may also want  join our developer chat on Telegram at <https://t.me/iscc_dev>.\n\n## License\n\nAll of documentation is licensed under the [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/).\n\nReference code is licensed under BSD-2-Clause.\n',
    'author': 'Titusz Pan',
    'author_email': 'tp@py7.de',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://iscc.codes/',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.6.1,<3.10',
}


setup(**setup_kwargs)
