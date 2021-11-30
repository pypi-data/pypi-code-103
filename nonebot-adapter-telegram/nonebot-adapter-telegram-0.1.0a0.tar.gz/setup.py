# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['nonebot', 'nonebot.adapters.telegram']

package_data = \
{'': ['*']}

install_requires = \
['aiofiles>=0.7.0,<0.8.0', 'nonebot2>=2.0.0a16,<3.0.0']

setup_kwargs = {
    'name': 'nonebot-adapter-telegram',
    'version': '0.1.0a0',
    'description': 'telegram adapter for nonebot2',
    'long_description': '# NoneBot-Adapter-Telegram\n\n_✨ telegram 协议适配 ✨_\n\n## Manual\n\n[使用指南](./MANUAL.md)\n\n## TODO\n\n- [ ] Inline Mode Support\n- [ ] Multiple Bot Support',
    'author': 'Jigsaw',
    'author_email': 'j1g5aw@foxmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://v2.nonebot.dev/',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7.3,<4.0.0',
}


setup(**setup_kwargs)
