# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['vhrun3',
 'vhrun3.app',
 'vhrun3.app.routers',
 'vhrun3.builtin',
 'vhrun3.ext',
 'vhrun3.ext.har2case',
 'vhrun3.ext.locust',
 'vhrun3.ext.uploader',
 'vhrun3.report',
 'vhrun3.report.allure_report',
 'vhrun3.report.html']

package_data = \
{'': ['*']}

install_requires = \
['httprunner==3.1.6', 'paramiko==2.6.0']

entry_points = \
{'console_scripts': ['vhar2case = vhrun3.cli:main_har2case_alias',
                     'vhmake = vhrun3.cli:main_make_alias',
                     'vhrun = vhrun3.cli:main_hrun_alias',
                     'vhrun3 = vhrun3.cli:main',
                     'vlocusts = vhrun3.ext.locust:main_locusts']}

setup_kwargs = {
    'name': 'vhrun3',
    'version': '1.3.1',
    'description': '',
    'long_description': '\n#### 介绍\n\n基于httprunner==3.1.6版本，根据特定需求二次定制开发\n\n##### 更新日志:\n###### 1.0.1\n- 1、保留2.x版本的用例分层机制，避免冗余出现api基本信息（url、headers、method等）\n- 2、除支持http和https协议外，支持SSH协议，可以远程执行shell命令、文件上传和下载\n- 3、兼容支持2.x测试报告，便于测试时调试\n- 4、数据驱动改成一个Class N个test_*用例方式，便于用例扫描成独立用例\n- 5、支持test_xx的__doc__自动生成，并支持config.variables和parameters变量解析\n- 6、yml中config中usefixtures字段，支持pytest指定添加fixture\n###### 1.1.3\n- 7、支持特定场景下的skipif代码生成\n###### 1.1.6\n- 8、allure报告增加详细步骤信息\n###### 1.1.9\n- 9、支持testcse级别的setup和teardown\n###### 1.2.0\n- 10、Testcae和TestStep支持skipIf\n###### 1.2.1\n- 11、allure报告中显示Method和url\n- 12、修复setup_hooks/teardown_hooks使用$request和$response出现的问题\n- 13、支持api中variables与teststep中variables进行合并\n- 14、setup_hooks/teardown_hooks中返回的变量可以之后的teststep所使用\n###### 1.2.2\n- 15、setup_hooks/teardown_hooks中返回的变量显示在allure报告的extract_values中\n- 16、支持循环执行teststep直到达到目标条件或超时退出\n###### 1.2.3\n- 17、循环增强：支持loop_for和loop_while\n- 18、环境变量带上进程号+线程号，避免pytest在使用并发插件时出现混乱\n###### 1.2.4\n- 19、修复v1.2.3中的bug\n###### 1.2.5\n- 20、teradown_hooks的执行放于extract之后，以便teardown_hooks可以使用extract后的变量\n###### 1.2.6\n- 21、loop_for支持递归嵌套\n###### 1.2.7\n- 22、修复allure.step中因“{}”.format引起的错误\n###### 1.2.8\n- 23、allure中的用例名称支持变量解析\n###### 1.3.1\n- 24、日志和allure报告添加validate描述\n- 25、parameter生成支持变量解析，修复单个字段时值不能为list的bug\n- 26、allure报告的validate_list优化\n- 27、allure报告增加setup_hooks和teardown_hooks详情\n#### 新增SSH部分示例：\n###### 1、执行shell命令\n```\nconfig:\n  name: demo - exec shell cmd\n  variables:\n    executor: ls\n    params: -alh\nteststeps:\n  - name: api -> shell\n    protocol: ssh\n    connection:   # 指定目标机器IP、Port、User和Password\n      ssh_ip: ${ENV(hostname)}  \n      ssh_port: ${ENV(ssh_port)}\n      ssh_user: ${ENV(ssh_user)}\n      ssh_password: ${ENV(ssh_password)}\n    request:\n      type: shell   # 指定类型为执行Shell命令\n      executor: $executor  # shell自带命令或可执行程序\n      params: $params # 字符串或字符串列表\n```\n###### 2、文件上传\n```\nconfig:\n  name: demo - upload file\nteststeps:\n  - name: api -> upload\n    protocol: ssh\n    connection:\n      ssh_ip: ${ENV(hostname)}\n      ssh_port: ${ENV(ssh_port)}\n      ssh_user: ${ENV(ssh_user)}\n      ssh_password: ${ENV(ssh_password)}\n    request:\n        type: upload # 指定类型为文件上传\n        local_path: $local_path  # 相对于本项目根目录的路径\n        remote_path: $remote_path  # 远程绝对路径\n```\n\n###### 3、文件下载\n```\nconfig:\n  name: demo - download file\nteststeps:\n  - name: api -> download\n    protocol: ssh\n    connection:\n      ssh_ip: ${ENV(hostname)}\n      ssh_port: ${ENV(ssh_port)}\n      ssh_user: ${ENV(ssh_user)}\n      ssh_password: ${ENV(ssh_password)}\n    request:\n        type: download # 指定类型为文件下载\n        local_path: $local_path  # 相对于本项目根目录的路径\n        remote_path: $remote_path  # 远程绝对路径\n```\n#### 参考：\n```\nhomepage = "https://github.com/httprunner/httprunner"\nrepository = "https://github.com/httprunner/httprunner"\ndocumentation = "https://docs.httprunner.org"\nblog = "https://debugtalk.com/\n```\n',
    'author': 'tigerjlx',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
