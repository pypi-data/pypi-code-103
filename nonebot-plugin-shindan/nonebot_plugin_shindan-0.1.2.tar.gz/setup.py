# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['nonebot_plugin_shindan']

package_data = \
{'': ['*']}

install_requires = \
['httpx>=0.19.0,<0.20.0',
 'lxml>=4.6.4,<5.0.0',
 'nonebot-adapter-cqhttp>=2.0.0-alpha.15,<3.0.0',
 'nonebot2>=2.0.0-alpha.15,<3.0.0',
 'playwright>=1.9.2,<2.0.0']

setup_kwargs = {
    'name': 'nonebot-plugin-shindan',
    'version': '0.1.2',
    'description': 'Nonebot2 plugin for using ShindanMaker',
    'long_description': None,
    'author': 'meetwq',
    'author_email': 'meetwq@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
