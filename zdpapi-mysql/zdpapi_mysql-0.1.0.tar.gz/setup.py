# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['zdpapi_mysql', 'zdpapi_mysql.pymysql', 'zdpapi_mysql.pymysql.constants']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'zdpapi-mysql',
    'version': '0.1.0',
    'description': '基于异步的快速操作MySQL的组件',
    'long_description': '# zapi_mysql\n基于异步的快速操作MySQL的组件\n\n使用pip安装\n```shell\npip install zapi_mysql\n```\n\n## 一、增删改数据\n\n### 1.1 创建表\n```python\nimport asyncio\nfrom zapi_mysql import Mysql\ndb = Mysql(host=\'127.0.0.1\',\n           port=3306,\n           user=\'root\',\n           password=\'root\',\n           db=\'test\')\n\n\nasync def test_example_execute(loop):\n    # 删除表\n    await db.connect()\n    sql = "DROP TABLE IF EXISTS user;"\n    \n    # 创建表\n    await db.execute(sql)\n    sql = """CREATE TABLE user\n                                  (id INT,\n                                  name VARCHAR(255),\n                                  PRIMARY KEY (id));"""\n    await db.execute(sql)\n    \n    # 插入SQL语句\n    sql = "INSERT INTO user VALUES(1,\'张三\')"\n    await db.execute(sql)\n\n\nloop = asyncio.get_event_loop()\nloop.run_until_complete(test_example_execute(loop))\n```\n\n### 1.2 插入数据\n```python\nimport asyncio\nfrom zapi_mysql import Mysql\ndb = Mysql(host=\'127.0.0.1\',\n           port=3306,\n           user=\'root\',\n           password=\'root\',\n           db=\'test\')\n\n\nasync def test_example_execute(loop):\n    # 插入SQL语句\n    sql = "INSERT INTO user VALUES(2,\'李四\')"\n    await db.execute(sql)\n\n\nloop = asyncio.get_event_loop()\nloop.run_until_complete(test_example_execute(loop))\n```\n\n### 1.3 批量插入数据\n```python\nimport asyncio\nfrom zapi_mysql import Mysql\ndb = Mysql(host=\'127.0.0.1\',\n           port=3306,\n           user=\'root\',\n           password=\'root\',\n           db=\'test\')\n\n\nasync def test_example_execute(loop):\n    # 插入SQL语句\n    data = [(4, \'gothic metal\'), (5, \'doom metal\'), (6, \'post metal\')]\n    sql = "INSERT INTO user VALUES(%s,%s)"\n    await db.execute(sql, data=data)\n\n\nloop = asyncio.get_event_loop()\nloop.run_until_complete(test_example_execute(loop))\n```\n\n## 二、查询数据\n\n### 2.1 查询所有数据\n```python\nimport asyncio\nfrom zapi_mysql import Mysql\ndb = Mysql(host=\'127.0.0.1\',\n           port=3306,\n           user=\'root\',\n           password=\'root\',\n           db=\'test\')\n\n\nasync def test_example_execute(loop):\n    # 插入SQL语句\n    sql = "SELECT id, name FROM user ORDER BY id"\n    result = await db.execute(sql)\n    print("查询结果：\\n", result)\n\n\nloop = asyncio.get_event_loop()\nloop.run_until_complete(test_example_execute(loop))\n```\n\n### 2.2 查询单条数据\n```python\nimport asyncio\nfrom zapi_mysql import Mysql\ndb = Mysql(host=\'127.0.0.1\',\n           port=3306,\n           user=\'root\',\n           password=\'root\',\n           db=\'test\')\n\n\nasync def test_example_execute(loop):\n    # 查询单条数据\n    sql = "SELECT id, name FROM user ORDER BY id"\n    result = await db.execute(sql, return_all=False)\n    print("查询结果：\\n", result)\n\n\nloop = asyncio.get_event_loop()\nloop.run_until_complete(test_example_execute(loop))\n```\n\n',
    'author': '张大鹏',
    'author_email': 'lxgzhw@163.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/zhangdapeng520/zdpapi_mysql',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
