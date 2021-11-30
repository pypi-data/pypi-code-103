# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src/plugins'}

packages = \
['nonebot_bison', 'nonebot_bison.admin_page', 'nonebot_bison.platform']

package_data = \
{'': ['*'], 'nonebot_bison.admin_page': ['dist/*']}

install_requires = \
['aiofiles>=0.7.0,<0.8.0',
 'apscheduler>=3.7.0,<4.0.0',
 'bs4>=0.0.1,<0.0.2',
 'expiringdict>=1.2.1,<2.0.0',
 'feedparser>=6.0.2,<7.0.0',
 'httpx>=0.16.1,<1.0.0',
 'nonebot-adapter-cqhttp>=2.0.0-alpha.15,<3.0.0',
 'nonebot2>=2.0.0-alpha.15,<3.0.0',
 'pillow>=8.1.0,<9.0.0',
 'pyjwt>=2.1.0,<3.0.0',
 'pyppeteer>=0.2.5,<0.3.0',
 'python-socketio>=5.4.0,<6.0.0',
 'tinydb>=4.3.0,<5.0.0']

setup_kwargs = {
    'name': 'nonebot-bison',
    'version': '0.4.1',
    'description': 'Subscribe message from social medias',
    'long_description': '<div align="center">\n<h1>Bison </br>通用订阅推送插件</h1>\n\n\n[![pypi](https://badgen.net/pypi/v/nonebot-bison)](https://pypi.org/project/nonebot-bison/)\n[![felinae98](https://circleci.com/gh/felinae98/nonebot-bison.svg?style=shield)](https://circleci.com/gh/felinae98/nonebot-bison)\n[![qq group](https://img.shields.io/badge/QQ%E7%BE%A4-868610060-orange )](https://qm.qq.com/cgi-bin/qm/qr?k=pXYMGB_e8b6so3QTqgeV6lkKDtEeYE4f&jump_from=webapi)\n\n[文档](https://nonebot-bison.vercel.app)|[开发文档](https://nonebot-bison.vercel.app/dev)\n</div>\n\n## 简介\n一款自动爬取各种站点，社交平台更新动态，并将信息推送到QQ的机器人。\n基于 [`NoneBot2`](https://github.com/nonebot/nonebot2 ) 开发（诞生于明日方舟的蹲饼活动）\n<details>\n<summary>本项目原名原名nonebot-hk-reporter</summary>\n\n寓意本Bot要做全世界跑的最快的搬运机器人，后因名字过于暴力改名\n\n</details>\n本项目名称来源于明日方舟角色拜松——一名龙门的信使，曾经骑自行车追上骑摩托车的德克萨斯\n\n支持的平台：\n* 微博\n* B站\n* RSS\n* 明日方舟\n  * 塞壬唱片新闻\n  * 游戏内公告\n  * 版本更新等通知\n* 网易云音乐\n  * 歌手发布新专辑\n  * 电台更新\n\n\n## 功能\n* 定时爬取指定网站\n* 通过图片发送文本，防止风控\n* 使用队列限制发送频率\n* 使用网页后台管理Bot订阅\n\n## 使用方法\n**!!注意，如果要使用后台管理功能请使用pypi版本或者docker版本，如果直接clone源代码\n需要按下面方式进行build**\n```bash\ncd ./admin-frontend\nyarn && yarn build\n```\n可以使用Docker，docker-compose，作为插件安装在nonebot中，或者直接运行  \n参考[文档](https://nonebot-bison.vercel.app/usage/#%E4%BD%BF%E7%94%A8)\n\n## FAQ\n1. 报错`TypeError: \'type\' object is not subscriptable`  \n    本项目使用了Python 3.9的语法，请将Python版本升级到3.9及以上，推荐使用docker部署\n2. bot不理我  \n    请确认自己是群主或者管理员，并且检查`COMMAND_START`环境变量是否设为`[""]`\n3. 微博漏订阅了\n    微博更新了新的风控措施，某些含有某些关键词的微博会获取不到。\n\n## 参与开发\n欢迎各种PR，参与开发本插件很简单，只需要对相应平台完成几个接口的编写就行。你只需要一点简单的爬虫知识就行。\n\n如果对整体框架有任何意见或者建议，欢迎issue。\n\n## 鸣谢\n* [`go-cqhttp`](https://github.com/Mrs4s/go-cqhttp)：简单又完善的 cqhttp 实现\n* [`NoneBot2`](https://github.com/nonebot/nonebot2)：超好用的开发框架\n* [`HarukaBot`](https://github.com/SK-415/HarukaBot/): 借鉴了大体的实现思路\n* [`rsshub`](https://github.com/DIYgod/RSSHub)：提供了大量的api\n\n## License\nMIT\n\n',
    'author': 'felinae98',
    'author_email': 'felinae225@qq.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/felinae98/nonebot-bison',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
