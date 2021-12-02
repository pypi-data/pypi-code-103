# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['mycqu', 'mycqu._lib_wrapper', 'mycqu.lib_wrapper', 'mycqu.utils']

package_data = \
{'': ['*']}

install_requires = \
['beautifulsoup4>=4,<5',
 'pycryptodome>=3,<4',
 'pydantic>=1,<2',
 'requests>=2,<3']

setup_kwargs = {
    'name': 'mycqu',
    'version': '0.1.0',
    'description': '重庆重庆大学新教务网及相关 api 的封装',
    'long_description': None,
    'author': 'Hagb',
    'author_email': 'hagb_green@qq.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
