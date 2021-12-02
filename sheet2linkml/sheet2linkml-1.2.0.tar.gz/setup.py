# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['sheet2linkml',
 'sheet2linkml.source',
 'sheet2linkml.source.gsheetmodel',
 'sheet2linkml.terminologies',
 'sheet2linkml.terminologies.tccm']

package_data = \
{'': ['*']}

install_requires = \
['PyYAML>=5.4.1,<6.0.0',
 'black>=21.9b0,<22.0',
 'linkml-runtime>=1.1.2,<2.0.0',
 'pygsheets>=2.0.4,<3.0.0',
 'python-dotenv>=0.15.0,<0.16.0',
 'requests>=2.26,<3.0',
 'setuptools>=52.0.0,<53.0.0']

entry_points = \
{'console_scripts': ['sheet2linkml = sheet2linkml.cli:main']}

setup_kwargs = {
    'name': 'sheet2linkml',
    'version': '1.2.0',
    'description': 'Google Sheets to LinkML generator for the CRDC-H model',
    'long_description': '# sheet2linkml\n\n[![PyPI version](https://badge.fury.io/py/sheet2linkml.svg)](https://badge.fury.io/py/sheet2linkml)\n\nA python package for converting the CRDC-H data model, which is currently stored in a \n[Google Sheet](https://docs.google.com/spreadsheets/d/1oWS7cao-fgz2MKWtyr8h2dEL9unX__0bJrWKv6mQmM4/). The command line utility built into the package can be used \nto generate a [LinkML](https://github.com/linkml/linkml) representation of the CRDC-H data model.\n\n## Installation Requirements and Pre-requisites\n\n- Python 3.7 or higher\n- [pyenv](https://github.com/pyenv/pyenv)\n    - If you do not have a version of Python greater than 3.9, it is recommended to use `pyenv` to be able to easily use and \nswitch between multiple Python versions.\n    - If you’re experiencing issues with pyenv on macOS, you can consider using [miniconda](https://docs.conda.io/en/latest/miniconda.html).\n- [poetry](https://github.com/python-poetry/poetry)\n    - One-time installation commands are available for [osx/linux/bash on windows](https://github.com/python-poetry/poetry#osx--linux--bashonwindows-install-instructions) and for [windows powershell](https://github.com/python-poetry/poetry#windows-powershell-install-instructions).\n\nIf you are using a Windows machine, typical bash programs will not work on `cmd` in the same way as they work in the Linux/MacOS terminals. To circumvent this, it is recommended that you use one of the following Bash on Windows strategies:\n- [WSL](https://www.howtogeek.com/249966/how-to-install-and-use-the-linux-bash-shell-on-windows-10/)\n- [Cygwin](https://cygwin.com/index.html)\n- [Git Bash](https://gitforwindows.org/) \n\nso you can easily execute the command line utilities that are described later in these docs.\n\n\n\n## Installing\n\nCreate and activate a Python 3.9+ virtual environment within which you can install the package:\n\n```shell\npython3 -m venv .venv\nsource .venv/bin/activate\npython -m pip install sheet2linkml\n```\n\n## Command Line Client Usage\n\nIdentify the Google Sheet that you want to convert to LinkML. Note that sheet2linkml is not currently a general-purpose Google Sheet to LinkML converter. It will only work with Google Sheets that have been written in a particular, currently undefined format.\n\nContact your CCDH colleagues to obtain the correct sheet ID and assert it either in a `.env` file or in the shell, like this:\n\n```shell\nexport CDM_GOOGLE_SHEET_ID=WbM2Jr869ofmdcSmhX_1E0aLWvnK2-gr47Mo_tzuQKWy\n```\n\nA `google_api_credentials.json` file is also required in the root of this repo. Documentation is forthcoming.\n\nAnd the user is responsible for defining \n- `~/path/to/crdch_model.yaml`\n- `~/path/to/logging.ini`\n    - `./logging.ini` may be adaquate for many users\n\n### Then perform the conversion:\n\n```shell\nsheet2linkml --output ~/path/to/crdch_model.yaml --logging-config ~/path/to/logging.ini\n```\n',
    'author': 'Gaurav Vaidya',
    'author_email': 'gaurav@renci.org',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/cancerDHC/sheet2linkml',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
