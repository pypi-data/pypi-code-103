# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['freelanceapi',
 'freelanceapi.hwm',
 'freelanceapi.msr',
 'freelanceapi.project',
 'freelanceapi.utils']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'freelanceapi',
    'version': '0.1.2b0',
    'description': 'FreelanceAPI is a module for reading & evaluating export files from the Freelance control system.',
    'long_description': '# FreecomAPI\n\n[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/release/python-360/)\n[![PyPI version](https://badge.fury.io/py/freelanceapi.svg)](https://badge.fury.io/py/freelanceapi)\n[![GitHub license](https://img.shields.io/github/license/DarkJumper/FreelanceAPI)](https://github.com/DarkJumper/FreelanceAPI/blob/main/LICENSE)\n\nWith the Freelance API an export file from the ABB Freelance control system can be evaluated.\n\n## It provides:\n\nMeanings of the Dict Keys:\n- KW: Key Word\n- LEN: Length of Dataset\n- NA: Next element available\n- MN: Measuring point name\n- MT: Module Type\n- ST: Short Text\n- LT: Long Text\n- AD: Area Definition\n- SB: Status Bit\n- VN: Variable Name\n- DT: Data Typ\n- VT: Variable Text\n- PI: Process image\n- EX: Exported Variable\n- VC: Variable(0) or Const (1)\n- FB: FBS Name\n- LB: Libary\n- DTMN: DTM Number\n- DTMC: DTM Config\n- QC: Quantity counter\n- FN: Function Name\n',
    'author': 'Peter Schwarz',
    'author_email': 'p.schwarz1994@outlook.de',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/DarkJumper/FreelanceAPI',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.9.1,<4.0.0',
}


setup(**setup_kwargs)
