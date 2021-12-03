# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['zdpapi',
 'zdpapi.api',
 'zdpapi.libs',
 'zdpapi.libs.fastapi',
 'zdpapi.libs.fastapi.dependencies',
 'zdpapi.libs.fastapi.middleware',
 'zdpapi.libs.fastapi.openapi',
 'zdpapi.libs.fastapi.security',
 'zdpapi.libs.starlette',
 'zdpapi.libs.starlette.middleware',
 'zdpapi.plugin']

package_data = \
{'': ['*']}

install_requires = \
['pydantic>=1.8.2,<2.0.0', 'uvicorn>=0.15.0,<0.16.0']

setup_kwargs = {
    'name': 'zdpapi',
    'version': '0.1.0',
    'description': '基于异步的快速开发RESTFUL API的极速后端框架',
    'long_description': '# zapi\n基于异步的快速开发RESTFUL API的极速后端框架\n\n安装方式：',
    'author': '张大鹏',
    'author_email': 'lxgzhw@163.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/zhangdapeng520/zapi',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
