# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['RPA', 'RPA.Windows', 'RPA.Windows.keywords', 'RPA.scripts']

package_data = \
{'': ['*']}

install_requires = \
['pynput-robocorp-fork>=4.0.0,<5.0.0',
 'robotframework-pythonlibcore>=3.0.0,<4.0.0',
 'robotframework>=4.0.0,!=4.0.1,<5.0.0',
 'rpaframework-core>=6.5.1,<7.0.0',
 'uiautomation>=2.0.15,<3.0.0']

extras_require = \
{':python_version >= "3.6" and python_version < "3.7"': ['dataclasses>=0.7,<0.8'],
 ':sys_platform == "win32"': ['comtypes==1.1.10', 'psutil>=5.8.0,<6.0.0']}

entry_points = \
{'console_scripts': ['windows-record = RPA.scripts.record:main']}

setup_kwargs = {
    'name': 'rpaframework-windows',
    'version': '1.4.0',
    'description': 'Windows library for RPA Framework',
    'long_description': 'rpaframework-windows\n====================\n\nThis library enables Windows automation for the  `RPA Framework`_\nlibraries based on `uiautomation`_ dependency.\n\n.. _RPA Framework: https://rpaframework.org\n.. _uiautomation: https://github.com/yinkaisheng/Python-UIAutomation-for-Windows\n',
    'author': 'RPA Framework',
    'author_email': 'rpafw@robocorp.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://rpaframework.org/',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.6.2,<4.0.0',
}


setup(**setup_kwargs)
