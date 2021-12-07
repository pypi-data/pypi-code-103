# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['zdpapi_file']

package_data = \
{'': ['*']}

install_requires = \
['pydantic>=1.8.2,<2.0.0', 'uvicorn>=0.15.0,<0.16.0']

setup_kwargs = {
    'name': 'zdpapi-file',
    'version': '0.1.0',
    'description': 'Python操作文件和文件夹的便捷组件库',
    'long_description': '# zdpapi_file\nPython操作文件和文件夹的便捷组件库\n\n项目地址：https://github.com/zhangdapeng520/zdpapi_file\n\n## 一、概述\n\n### 1.1 功能\n\n- 查看文件夹占用磁盘大小\n\n\n## 二、快速入门\n\n### 2.1 查看文件夹占用磁盘大小\n```python\nfrom zdpapi_file import Directory\n\ndef test_disk_usage(path):\n    dir = Directory(path)\n    print(dir.disk_usage())\n\nif __name__ == "__main__":\n    test_disk_usage("D:\\\\BaiduNetdiskWorkspace\\\\文档")\n```\n',
    'author': '张大鹏',
    'author_email': 'lxgzhw@163.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/zhangdapeng520/zdpapi_file',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
