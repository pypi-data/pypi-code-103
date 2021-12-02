# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['mycqu', 'mycqu._lib_wrapper', 'mycqu.utils']

package_data = \
{'': ['*']}

install_requires = \
['beautifulsoup4>=4,<5',
 'pycryptodome>=3,<4',
 'pydantic>=1,<2',
 'requests>=2,<3']

setup_kwargs = {
    'name': 'mycqu',
    'version': '0.2.1',
    'description': '重庆重庆大学新教务网及相关 api 的封装',
    'long_description': '# pymycqu\n\n这个库对重庆大学 <https://my.cqu.edu.cn> 和统一身份认证的部分 web api 进行了封装，同时整理了相关数据模型。\n\nWork in progress... 欢迎反馈和补充\n\n感谢 <https://github.com/CQULHW/CQUQueryGrade> 项目提供了 <https://my.cqu.edu.cn> 的登陆方式。\n\n## 安装\n\n```bash\npip install mycqu\n```\n\n## 例子及文档\n\n见 <https://pymycqu.hagb.name>.\n\n## 许可\n\nAGPL 3.0\n',
    'author': 'Hagb',
    'author_email': 'hagb_green@qq.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://pymycqu.hagb.name',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
