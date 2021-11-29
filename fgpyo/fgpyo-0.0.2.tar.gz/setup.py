# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['fgpyo', 'fgpyo.tests', 'fgpyo.util', 'fgpyo.util.tests']

package_data = \
{'': ['*']}

install_requires = \
['attrs>=19.3.0', 'samwell>=0.0.2']

extras_require = \
{':python_version < "3.8"': ['typing_extensions>=3.7.4',
                             'typing_inspect>=0.3.1']}

setup_kwargs = {
    'name': 'fgpyo',
    'version': '0.0.2',
    'description': 'Python bioinformatics and genomics library',
    'long_description': '\n[![Language][language-badge]][language-link]\n[![Code Style][code-style-badge]][code-style-link]\n[![Type Checked][type-checking-badge]][type-checking-link]\n[![PEP8][pep-8-badge]][pep-8-link]\n[![Code Coverage][code-coverage-badge]][code-coverage-link]\n[![License][license-badge]][license-link]\n\n---\n\n[![Python package][python-package-badge]][python-package-link]\n[![PyPI version][pypi-badge]][pypi-link]\n[![PyPI download total][pypi-downloads-badge]][pypi-downloads-link]\n\n---\n\n[language-badge]:       http://img.shields.io/badge/language-python-brightgreen.svg\n[language-link]:        http://www.python.org/\n[code-style-badge]:     https://img.shields.io/badge/code%20style-black-000000.svg\n[code-style-link]:      https://black.readthedocs.io/en/stable/ \n[type-checking-badge]:  http://www.mypy-lang.org/static/mypy_badge.svg\n[type-checking-link]:   http://mypy-lang.org/\n[pep-8-badge]:          https://img.shields.io/badge/code%20style-pep8-brightgreen.svg\n[pep-8-link]:           https://www.python.org/dev/peps/pep-0008/\n[code-coverage-badge]:  https://codecov.io/gh/fulcrumgenomics/fgpyo/branch/master/graph/badge.svg\n[code-coverage-link]:   https://codecov.io/gh/fulcrumgenomics/fgpyo\n[license-badge]:        http://img.shields.io/badge/license-MIT-blue.svg\n[license-link]:         https://github.com/fulcrumgenomics/fgpyo/blob/master/LICENSE\n[python-package-badge]: https://github.com/fulcrumgenomics/fgpyo/workflows/Python%20package/badge.svg\n[python-package-link]:  https://github.com/fulcrumgenomics/fgpyo/actions?query=workflow%3A%22Python+package%22\n[pypi-badge]:           https://badge.fury.io/py/fgpyo.svg\n[pypi-link]:            https://pypi.python.org/pypi/fgpyo\n[pypi-downloads-badge]: https://img.shields.io/pypi/dm/fgpyo\n[pypi-downloads-link]:  https://pypi.python.org/pypi/fgpyo\n\n# fgpyo\n\n`pip install fgpyo`\n\n**Requires python 3.6+**\n\n# Getting Setup\n\n[Poetry][poetry-link] is used to manage the python development environment. \n\nA simple way to create an environment with the desired version of python and poetry is to use [conda][conda-link].  E.g.:\n\n```bash\nconda create -n fgpyo python=3.6 poetry\nconda activate fgpyo\npoetry install\n```\n\nIf, during `poetry install` on Mac OS X errors are encountered running gcc/clang to build `pybedtools` or other packages with native code, try setting the following and re-running `poetry install`:\n```bash\nexport CFLAGS="-stdlib=libc++"\n``` \n\n[poetry-link]: https://github.com/python-poetry/poetry\n[conda-link]:  https://docs.conda.io/en/latest/miniconda.html\n',
    'author': 'Nils Homer',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/fulcrumgenomics/fgpyo',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.6.0',
}


setup(**setup_kwargs)
