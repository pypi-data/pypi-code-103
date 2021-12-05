# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['unicodedata_reader']

package_data = \
{'': ['*']}

install_requires = \
['platformdirs>=2.2.0,<3.0.0']

entry_points = \
{'console_scripts': ['unicodedata-reader = unicodedata_reader.__main__:main']}

setup_kwargs = {
    'name': 'unicodedata-reader',
    'version': '0.1.7',
    'description': '',
    'long_description': '[![CI](https://github.com/kojiishi/unicodedata-reader/actions/workflows/ci.yml/badge.svg)](https://github.com/kojiishi/unicodedata-reader/actions/workflows/ci.yml)\n[![PyPI](https://img.shields.io/pypi/v/unicodedata-reader.svg)](https://pypi.org/project/unicodedata-reader/)\n[![Dependencies](https://badgen.net/github/dependabot/kojiishi/unicodedata-reader)](https://github.com/kojiishi/unicodedata-reader/network/updates)\n\n\n# unicodedata-reader\n\nThis package reads and parses the [Unicode Character Database] files.\n\nMany of them are available in the [unicodedata] module,\nor in other 3rd party modules.\nWhen the desired data is not in any existing modules,\nsuch as the [Line_Break property] or the [Vertical_Orientation property],\nthis package can read the data files\nat <https://www.unicode.org/Public/UNIDATA/>.\n\nThis package can also generate JavaScript functions\nthat can read the property values of the [Unicode Character Database]\nin browsers.\nPlease see the [JavaScript] section below.\n\n[General_Category property]: http://unicode.org/reports/tr44/#General_Category\n[Line_Break property]: http://unicode.org/reports/tr44/#Line_Break\n[Unicode Character Database]: https://unicode.org/reports/tr44/\n[unicodedata]: https://docs.python.org/3/library/unicodedata.html\n[Vertical_Orientation property]: http://unicode.org/reports/tr44/#Vertical_Orientation\n\n## Install\n\n```sh\npip install unicodedata-reader\n```\nIf you want to clone and install using [poetry]:\n```sh\ngit clone https://github.com/kojiishi/unicodedata-reader\ncd unicodedata-reader\npoetry install\npoetry shell\n```\n\n[poetry]: https://github.com/python-poetry/poetry\n\n\n## Python\n\n```python\nimport unicodedata_reader\n\nreader = unicodedata_reader.UnicodeDataReader.default\nlb = reader.line_break()\nprint(lb.value(0x41))\n```\nThe example above prints `AL`,\nthe [Line_Break property] value for U+0041.\nPlease also see [line_break_test.py] for more usages.\n\n[line_break_test.py]: https://github.com/kojiishi/unicodedata-reader/blob/main/tests/line_break_test.py\n\n## JavaScript\n[JavaScript]: #javascript\n\nThe [`UnicodeDataCompressor` class] in this package\ncan generate JavaScript functions that can read the property values\nof the [Unicode Character Database] in browsers.\n\nFollowing examples are available in the "`js`" directory:\n* [GeneralCategory.js] is a generated JavaScript file\n  for the Unicode [General_Category property].\n* [LineBreak.js] is a generated JavaScript file\n  for the Unicode [Line_Break property].\n* [LineBreak.html] for an example usage of [LineBreak.js].\n\nThe following command generates a JavaScript file for the [Line_Break property]\nusing `js/template.js` as the template file:\n```sh\nunicodedata-reader lb -t js/template.js\n```\n\n[`UnicodeDataCompressor` class]: https://github.com/kojiishi/unicodedata-reader/blob/main/unicodedata_reader/compressor.py\n[GeneralCategory.js]: https://github.com/kojiishi/unicodedata-reader/blob/main/js/GeneralCategory.js\n[LineBreak.html]: https://github.com/kojiishi/unicodedata-reader/blob/main/js/LineBreak.html\n[LineBreak.js]: https://github.com/kojiishi/unicodedata-reader/blob/main/js/LineBreak.js\n',
    'author': 'Koji Ishii',
    'author_email': 'kojii@chromium.org',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/kojiishi/unicodedata-reader',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8',
}


setup(**setup_kwargs)
