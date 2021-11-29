# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['jalali_pandas']

package_data = \
{'': ['*']}

install_requires = \
['jdatetime>=3.6.4,<4.0.0']

setup_kwargs = {
    'name': 'jalali-pandas',
    'version': '0.1.3',
    'description': 'A Pandas extension to make work with Jalali Date easier.',
    'long_description': '[![HitCount](http://hits.dwyl.com/ghodsizadeh/jalali-pandas.svg)](http://hits.dwyl.com/ghodsizadeh/jalali-pandas)\n![PyPI - Downloads](https://img.shields.io/pypi/dw/tehran_stocks.svg?color=blue)\n[![PyPI version](https://badge.fury.io/py/jalali-pandas.svg)](https://badge.fury.io/py/jalali-pandas)\n[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/python/black)\n[![codecov](https://codecov.io/gh/ghodsizadeh/jalali-pandas/branch/main/graph/badge.svg?token=LWQ85TN0NU)](https://codecov.io/gh/ghodsizadeh/jalali-pandas)\n[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)\n[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/ghodsizadeh/jalali-pandas/blob/main/examples/basic_usage.ipynb)\n![GitHub Repo stars](https://img.shields.io/github/stars/ghodsizadeh/jalali-pandas?logoColor=blue&style=social)\n\n# Jalali Pandas Extentsion\n\n> A pandas extension that solves all problems of Jalai/Iraninan/Shamsi dates\n\n![Jalali Pandas python package](/assets/github-jalali-pandas.png)\n\n## Features\n\n#### Series Extenstion\n\n- Convert _string_ to _Jalali_ date `1388/03/25` --> `jdatetime(1388,3,25,0,0)`\n- Convert _Georgian_ date to _Jalali_ date `datetime(2019,11,17,0,0)` --> `jdatetime(1398,8,26,0,0)`\n- Convert _Jalali_ date to _Georgian_ date `jdatetime(1398,10,18,0,0)` --> `datetim(2020,1,8,6,19)`\n\n#### DataFrame extenstion\n\n- Support grouping by _Jalali_ date\n- Group by year, month, days, ...\n- Shortcuts for groups: `ymd` for `[\'year\',\'month\',\'day\']` and more\n- Resampling: Convenience method for frequency conversion and resampling of time series but in _Jalali_ dateformat. (comming soon)\n\n## Installation\n\n    pip install -U jalali-pandas\n\n## Usage\n\nJust import jalali-pandas and use pandas just use `.jalali` as a method for series and dataframes. Nothin outside pandas.\n\n> `jalali-pandas` is an extentsion for pandas, that add a mehtod for series/columns and dataframes.\n\n### Series\n\n```python\nimport pandas as pd\nimport jalali_pandas\n\n# create dataframe\ndf = pd.DataFrame({"date": pd.date_range("2019-01-01", periods=10, freq="D")})\n\n# convert to jalali\ndf["jdate"] = df["date"].jalali.to_jalali()\n\n# convert to gregorian\ndf["gdate"] = df["jdate"].jalali.to_georgian()\n\n# parse string to jalali\ndf1 = pd.DataFrame({"date": ["1399/08/02", "1399/08/03", "1399/08/04"]})\ndf1["jdate"] = df1["date"].jalali.parse_jalali("%Y/%m/%d")\n\n\n# get access to jalali year,quarter ,month, day and weekday\ndf[\'year\'] = df["jdate"].jalali.year\ndf[\'month\'] = df["jdate"].jalali.month\ndf[\'quarter\'] = df["jdate"].jalali.quarter\ndf[\'day\'] = df["jdate"].jalali.day\ndf[\'weekday\'] = df["jdate"].jalali.weekday\n\n```\n\n### DataFrame\n\n```python\n\nimport pandas as pd\nimport jalali_pandas\n\ndf = pd.DataFrame(\n    {\n    "date": pd.date_range("2019-01-01", periods=10, freq="M"),\n    "value": range(10),\n    }\n)\n# make sure to create a column with jalali datetime format. (you can use any name)\ndf["jdate"] = df["date"].jalali.to_jalali()\n\n\n# group by jalali year\ngp = df.jalali.groupby("year")\ngp.sum()\n\n#group by month\nmean = df.jalali.groupby(\'mean\')\n\n#groupby year and month and day\nmean = df.jalali.groupby(\'ymd\')\n# or\nmean = df.jalali.groupby([\'year\',\'month\',\'day\'])\n\n\n#groupby year and quarter\nmean = df.jalali.groupby(\'yq\')\n# or\nmean = df.jalali.groupby([\'year\',\'quarter\'])\n```\n\n## ToDos:\n\n- [x] add Georgian to Jalali Conversion\n- [x] add Jalali to Georgian Conversion\n- [ ] add support for sampling\n- [x] add date parser from other columns\n- [x] add date parser from string\n',
    'author': 'Mehdi Ghodsizadeh',
    'author_email': 'mehdi.ghodsizadeh@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://ghodsizadeh.github.io/jalali-pandas/',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
