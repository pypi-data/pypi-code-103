# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['zdpapi_router']

package_data = \
{'': ['*']}

install_requires = \
['zdpapi-mysql>=1.0.2,<2.0.0', 'zdpapi>=0.1.0,<0.2.0']

setup_kwargs = {
    'name': 'zdpapi-router',
    'version': '1.0.0',
    'description': '快速开发后端API的路由组件，支持自动生成CRUD接口',
    'long_description': '# zdpapi_router\n快速开发后端API的路由组件，支持自动生成CRUD接口\n\n说明：此项目基于zdpapi和zdpapi_mysql构建，如果使用有困难的同学，可以先去看这两个框架\n- zdpapi项目地址：https://github.com/zhangdapeng520/zdpapi\n- zdpapi_mysql项目地址：https://github.com/zhangdapeng520/zdpapi_mysql\n\n本项目地址：https://github.com/zhangdapeng520/zdpapi_router\n\n功能：\n- 自动生成新增单条数据路由\n- 自动生成新增多条数据路由\n- 自动生成删除单条数据路由\n- 自动生成删除多条数据路由\n- 自动生成修改单条数据路由\n- 自动生成修改多条数据路由\n- 自动生成查询单条数据路由\n- 自动生成查询多条数据路由\n- 自动生成分页查询多条数据路由\n\n## 一、快速入门\n\n### 1.1 安装\n```shell\npip install zdpapi_router\n```\n\n### 1.2 说明\n如果您要直接使用示例代码，一定要确保本地安装了MySQL数据库，且创建了名为test的数据库。同时在test数据库中存在user表，该表有id和name两个字段。\n\n如果您学习过我的另一个项目zdpapi_mysql，则直接运行里面的示例代码即可。\n\n### 1.3 入门案例\n\n将下面的代码复制到main.py中\n```python\nfrom zdpapi_router import CRUDRouter\nfrom zdpapi import ZApi\nfrom pydantic import BaseModel\n\napp = ZApi()\n\n\nclass UserSchema(BaseModel):\n    id: int  # 必须包含ID，批量更新的时候要用到\n    name: str\n\n\nmysql_config = {\n    "host": \'127.0.0.1\',\n    "port": 3306,\n    "user": \'root\',\n    "password": \'root\',\n    "db": \'test\'\n}\nrouter = CRUDRouter(mysql_config=mysql_config,\n                    table_name="user",\n                    columns=["name"],\n                    chinese_name="用户",\n                    schema=UserSchema)\napp = router.register(app)\n\nif __name__ == \'__main__\':\n    import uvicorn\n\n    uvicorn.run("main:app", reload=True)\n```\n\n运行\n```shell\npython main.py\n```\n\n访问：http://127.0.0.1:8000/docs\n\n',
    'author': '张大鹏',
    'author_email': 'lxgzhw@163.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/zhangdapeng520/zdpapi_router',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
