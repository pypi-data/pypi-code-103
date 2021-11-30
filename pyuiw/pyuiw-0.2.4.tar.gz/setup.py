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
    'version': '0.2.4',
    'description': 'Command Line File Watcher for Qt ui file to python file.',
    'long_description': '# pyuiw\n\n[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/FXTD-ODYSSEY/pyuiw/master.svg)](https://results.pre-commit.ci/latest/github/FXTD-ODYSSEY/pyuiw/master)\n[![python version](https://img.shields.io/pypi/pyversions/pyuiw)](https://img.shields.io/pypi/pyversions/pyuiw)\n[![PyPI version](https://img.shields.io/pypi/v/pyuiw?color=green)](https://badge.fury.io/py/pyuiw)\n[![Documentation Status](https://readthedocs.org/projects/pyuiw/badge/?version=master)](https://pyuiw.readthedocs.io/en/master/?badge=master)\n![Downloads Status](https://img.shields.io/pypi/dw/pyuiw)\n![License](https://img.shields.io/pypi/l/pyuiw)\n![pypi format](https://img.shields.io/pypi/format/pyuiw)\n[![Downloads](https://pepy.tech/badge/pyuiw)](https://pepy.tech/badge/pyuiw)\n[![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg)](https://github.com/loonghao/pyuiw/graphs/commit-activity)\n\nCommand Line Watcher for auto compile Qt ui to python file.\n\nOriginal Tool Source from [pyside2-tools](https://github.com/pyside/pyside2-tools) `pyside2uic`\nI modified some code for customization.\n\n## Install pyuiw\n\n```\npip install pyuiw\n```\n\n## How to Use\n\n\n```\npython -m pyuiw\npyuiw\n```\n\ntwo command run the same alternatively.\n\n![demo](./images/demo.gif)\n\n```\npyuiw -h\n```\n\nrun this command can show up the help documentation.\n\n```\nusage: pyuiw [-h] [-p] [-o FILE] [-x] [-d] [-i N] [--from-imports] [-nq] [--QtModule module] [-nb] [-ni] [-ts TS] [-w WATCH [WATCH ...]] [-e EXCLUDE [EXCLUDE ...]] [-c FILE]\n\nQt User Interface Compiler version , running on PySide2 5.15.2.\nCommand Line Watcher for auto compile Qt ui to python file.\n\nUsage Example:\n\noptional arguments:\n  -h, --help            show this help message and exit\n  -p, --preview         show a preview of the UI instead of generating code\n  -o FILE, --output FILE\n                        write generated code to FILE instead of stdout\n                        <EXP> to define a output expression (default: <${ui_dir}/${ui_name}_ui.py>)\n                        ${ui_dir} - input python directory path\n                        ${ui_name} - input python file name\n  -x, --execute         generate extra code to test and display the class\n  -d, --debug           show debug output\n  -i N, --indent N      set indent width to N spaces, tab if N is 0 (default: 4)\n\nCode generation options:\n  --from-imports        generate imports relative to \'.\'\n  -nq, --no-useQt       ignore Qt.py module for Qt compat\n  --QtModule module     customize import Qt module name (default: Qt) | only work in --no-useQt flag set\n  -nb, --no-black       ignore black format code\n  -ni, --no-isort       ignore isort format code\n  -ts TS, --gen-ts TS   generate ts file for i18n | support <EXP> like --output\n\nWatcher options:\n  -w WATCH [WATCH ...], --watch WATCH [WATCH ...]\n                        watch files or directories\n  -e EXCLUDE [EXCLUDE ...], --exclude EXCLUDE [EXCLUDE ...]\n                        exclude files glob expression\n  -c FILE, --config FILE\n                        read specific config file\n```\n\n## Configuration\n\n`pyuiw` would read the `pyproject.toml` by default or you can set the `--config` flag to read specific config file.\n\nhere is the default options in config file.\n```toml\n[tool.pyuiw]\nQtModule = "Qt"\nexclude = [] # using glob pattern for exclude\nuseQt = true\nwatch = []\nexecute = true\ndebug = false\nfrom_imports = false\npreview = false\nindent = 4\noutput = "<${ui_dir}/${ui_name}_ui.py>"\nblack = true\nisort = true\n```\n\nhere is a example setup.\n\n```toml\n[tool.pyuiw]\nexclude = ["*launcher*"] # exclude file contain `launcher`\nwatch = ["./tests/ui","./test2/test.ui"] # read the file or directory get all the `.ui` file for watch\n```\n\n## TodoList\n\n- [x] import code to the top (implement isort)\n- [x] black format code\n- [x] poetry pypi python package\n- [x] poetry command line tool\n- [x] add pytest\n- [x] auto create ts file\n- [x] shield.io icon\n- [ ] add sphinx docs\n\nuic enhance\n\n- [x] implement Qt.py for `QApplication.translate`\n- [x] customize import\n- [x] modern signal connections\n- [x] designer theme to standard icon set\n',
    'author': 'timmyliang',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/FXTD-ODYSSEY/pyuiw',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6.2,<3.10',
}


setup(**setup_kwargs)
