# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pyuiw',
 'pyuiw.uic',
 'pyuiw.uic.Compiler',
 'pyuiw.uic.port_v2',
 'pyuiw.uic.port_v3',
 'pyuiw.uic.widget-plugins']

package_data = \
{'': ['*']}

install_requires = \
['PySide2>=5.15.2,<6.0.0',
 'Qt.py>=1.3.6,<2.0.0',
 'black>=21.11b1,<22.0',
 'isort>=5.10.1,<6.0.0',
 'toml>=0.10.2,<0.11.0']

entry_points = \
{'console_scripts': ['pyuiw = pyuiw.__main__:PyUIWatcherCli']}

setup_kwargs = {
    'name': 'pyuiw',
    'version': '0.1.0',
    'description': 'Command Line File Watcher for Qt ui file to python file.',
    'long_description': '# pyuiw\n\nCommand Line Watcher for auto compile Qt ui to python file.\n\n## Install\n\n```\npip install pyuiw\n```\n\n\n## How to Use\n\n\n\n## TodoList\n\n- [x] import code to the top (implement isort)\n- [x] black format code\n- [x] implement Qt.py for `QApplication.translate`\n- [x] customize import\n- [x] poetry pypi python package\n- [x] poetry command line tool\n- [ ] unittest\n',
    'author': 'timmyliang',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6.2,<3.10',
}


setup(**setup_kwargs)
