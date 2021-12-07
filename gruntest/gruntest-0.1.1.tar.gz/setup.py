# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['gruntest']

package_data = \
{'': ['*']}

install_requires = \
['allure-pytest>=2.9.45,<3.0.0',
 'jsonpath>=0.82,<0.83',
 'pytest>=6.2.5,<7.0.0',
 'requests>=2.26.0,<3.0.0']

setup_kwargs = {
    'name': 'gruntest',
    'version': '0.1.1',
    'description': 'graphql & restful / http(s) tools',
    'long_description': '# 前置\n1. 安装allure并配置好环境变量\n2. 项目根目录新建 hooks.py 实现动态扩展函数\n3. 编写测试文件代码\n4. 执行测试\n\n# 作用\ngraphql, restful \nHTTP/HTTPS 接口测试工具，需要编写代码\n\n# example\n\n```python\n# testcase.py\n\nfrom gruntest.grunner import Grunner\nfrom gruntest.schemas import Config, TestStep, RequestSchema\n\n\nclass TestRunner(Grunner):\n    config = Config(\n        base_header={"Host": "49.232.203.244:1339"}\n    )\n    steps = [\n        TestStep(\n            name=\'百度\',\n            request=RequestSchema(\n                url=\'http://www.httpbin.org/get\',\n                method=\'get\',\n                headers={"token": "123"},\n                params={"limit": 5, "page": 1}\n            ),\n            extra={"code": "$.args.limit"}\n        ),\n        TestStep(\n            name=\'百度\',\n            request=RequestSchema(\n                url=\'http://www.httpbin.org/get\',\n                method=\'get\',\n                headers={"token": "123"},\n                params={"limit": 5, "page": "${sum2(\'$code\')}"}\n            ),\n            extra={"code": "$.args.limit"},\n            expect={"$.code": "code"}\n        )\n    ]\n```',
    'author': 'zy7y',
    'author_email': '396667207@qq.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
