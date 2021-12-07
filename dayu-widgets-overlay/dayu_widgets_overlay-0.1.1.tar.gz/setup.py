# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['dayu_widgets_overlay']

package_data = \
{'': ['*']}

install_requires = \
['Qt.py>=1.3.6,<2.0.0', 'dayu-path>=0.5.2,<0.6.0', 'six>=1.16.0,<2.0.0']

extras_require = \
{':python_version == "2.7"': ['singledispatch>=3.7.0,<4.0.0']}

setup_kwargs = {
    'name': 'dayu-widgets-overlay',
    'version': '0.1.1',
    'description': 'dayu_widgets MOverlay Widget for QtDesigner',
    'long_description': '# dayu_widgets_overlay\n\nPython Qt Overlay Widget as a [dayu_widgets](https://github.com/phenom-films/dayu_widgets) plugin\n\n## How it work\n\n![designer](./images/designer.png)\n\n![demo](https://cdn.jsdelivr.net/gh/FXTD-odyssey/FXTD-odyssey.github.io@master/post_img/1ba28015/09.gif)\n\noverlay the widget onto the other widget and resize together\nmuch easy to add and maintain instead of create a New type of widget.\n\n## How to use\n\n```cmd\npip install dayu_widgets_overlay\n```\n\n```Python\nfrom dayu_widgets_overlay import MOverlay\n```\n\nIn Qt Designer, you can extend a QWidget into MOverlay\n![designer](./images/01.png)\n\n\n## QtDesigner Property\n\n`direction` : `E` `S` `W` `N`\n\n`stretch` (optional - default: Auto) : `NoStretch` `Vertical` `Horizontal` `Center` `Auto`\n\n![designer](./images/02.png)\n\n---\n\nSee my blog article for more details in chinese\n\nhttps://blog.l0v0.com/posts/1ba28015.html\n',
    'author': 'timmyliang',
    'author_email': '820472580@qq.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*, !=3.4.*, !=3.5.*',
}


setup(**setup_kwargs)
