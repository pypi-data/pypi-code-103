# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['glQiwiApi',
 'glQiwiApi.contrib',
 'glQiwiApi.core',
 'glQiwiApi.core.abc',
 'glQiwiApi.core.dispatcher',
 'glQiwiApi.core.dispatcher.class_based',
 'glQiwiApi.core.dispatcher.webhooks',
 'glQiwiApi.core.dispatcher.webhooks.views',
 'glQiwiApi.core.session',
 'glQiwiApi.core.synchronous',
 'glQiwiApi.ext',
 'glQiwiApi.plugins',
 'glQiwiApi.plugins.telegram',
 'glQiwiApi.qiwi',
 'glQiwiApi.types',
 'glQiwiApi.types.arbitrary',
 'glQiwiApi.types.qiwi',
 'glQiwiApi.types.yoomoney',
 'glQiwiApi.utils',
 'glQiwiApi.yoo_money']

package_data = \
{'': ['*']}

install_requires = \
['aiohttp>=3.8.0,<4.0.0',
 'pydantic==1.8.2',
 'pytz==2021.3',
 'wheel>=0.36.2,<0.37.0']

extras_require = \
{':python_version <= "3.7"': ['typing_extensions>=3.10.0.2,<4.0.0.0']}

setup_kwargs = {
    'name': 'glqiwiapi',
    'version': '1.1.4',
    'description': 'The ultrarapid and multifunctional wrapper over QIWI and YooMoney',
    'long_description': '<h2 align="center">\n<img src="https://github.com/GLEF1X/glQiwiApi/blob/master/docs/static/logo.png" width="200"></img>\n\n\n[![PyPI version](https://img.shields.io/pypi/v/glQiwiApi.svg)](https://pypi.org/project/glQiwiApi/) [![Code Quality Score](https://www.code-inspector.com/project/20780/score/svg)](https://frontend.code-inspector.com/public/project/20780/glQiwiApi/dashboard) ![Code Grade](https://www.code-inspector.com/project/20780/status/svg) ![Downloads](https://img.shields.io/pypi/dm/glQiwiApi) ![docs](https://readthedocs.org/projects/pip/badge/?version=latest)\n[![Language grade: Python](https://img.shields.io/lgtm/grade/python/g/GLEF1X/glQiwiApi.svg?logo=lgtm&logoWidth=18)](https://lgtm.com/projects/g/GLEF1X/glQiwiApi/context:python) [![CodeFactor](https://www.codefactor.io/repository/github/glef1x/glqiwiapi/badge)](https://www.codefactor.io/repository/github/glef1x/glqiwiapi)\n![codecov](https://codecov.io/gh/GLEF1X/glQiwiApi/branch/dev-1.x/graph/badge.svg?token=OD538HKV15)\n![CI](https://github.com/GLEF1X/glQiwiApi/actions/workflows/tests.yml/badge.svg) ![mypy](https://img.shields.io/badge/%20type_checker-mypy-%231674b1?style=flat) [![Downloads](https://pepy.tech/badge/glqiwiapi/month)](https://pepy.tech/project/glqiwiapi) [![Downloads](https://pepy.tech/badge/glqiwiapi)](https://pepy.tech/project/glqiwiapi)\n\n<img src="https://github.com/GLEF1X/glQiwiApi/blob/master/demo.gif"/>\n</h2>\n\n## 🌎Official api resources:\n\n* 🎓 __Documentation: [here](https://glqiwiapi.readthedocs.io/en/latest/)__\n* 🖱️ __Developer\n  contacts: [![Dev-Telegram](https://img.shields.io/badge/Telegram-blue.svg?style=flat-square&logo=telegram)](https://t.me/GLEF1X)__\n\n## 🐦Dependencies\n\n| Library |                       Description                       |\n|:-------:|:-------------------------------------------------------:|\n|aiohttp  | Asynchronous HTTP Client/Server for asyncio and Python. |\n|aiofiles |            saving receipts in pdf(Optional)             |\n|pydantic |    Json data validator. Very fast instead of custom     |\n',
    'author': 'Gleb Garanin',
    'author_email': 'glebgar567@gmail.com',
    'maintainer': 'GLEF1X',
    'maintainer_email': 'glebgar567@gmail.com',
    'url': 'https://github.com/GLEF1X/glQiwiApi',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
