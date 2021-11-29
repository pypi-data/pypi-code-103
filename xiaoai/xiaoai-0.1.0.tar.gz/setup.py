# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['xiaoai']

package_data = \
{'': ['*']}

install_requires = \
['httpx']

setup_kwargs = {
    'name': 'xiaoai',
    'version': '0.1.0',
    'description': '小爱音箱非官方SDK。',
    'long_description': '# xiaoai\n\n小爱音箱非官方SDK。\n',
    'author': 'long2ice',
    'author_email': 'long2ice@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/long2ice/xiaoai',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
