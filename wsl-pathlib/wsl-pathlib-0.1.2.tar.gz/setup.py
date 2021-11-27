# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['wsl_pathlib']

package_data = \
{'': ['*']}

install_requires = \
['flake8==3.9']

setup_kwargs = {
    'name': 'wsl-pathlib',
    'version': '0.1.2',
    'description': 'extend to pathlib.Path to add the attribute wsl_path and win_path that holds respectively the  WSL (Windows Subsystem for Linux) representation and Windows representation of that path.',
    'long_description': '# wsl-pathlib\n\n[![Build Status](https://github.com/psychonaute/wsl-pathlib/workflows/test/badge.svg?branch=master&event=push)](https://github.com/psychonaute/wsl-pathlib/actions?query=workflow%3Atest)\n[![codecov](https://codecov.io/gh/psychonaute/wsl-pathlib/branch/master/graph/badge.svg)](https://codecov.io/gh/psychonaute/wsl-pathlib)\n[![Python Version](https://img.shields.io/pypi/pyversions/wsl-pathlib.svg)](https://pypi.org/project/wsl-pathlib/)\n[![wemake-python-styleguide](https://img.shields.io/badge/style-wemake-000000.svg)](https://github.com/wemake-services/wemake-python-styleguide)\n\nExtend `pathlib.Path` by addding the properties `wsl_path` and `win_path` that holds respectively the  WSL (Windows Subsystem for Linux) and Windows representation of the `Path` object.\n\n\n## Features\n- Lazy loading of the wsl_path and win_path properties on first access.\n- Base `Path` object remains fully functional.\n- Obviously works on both WSL and Windows side.\n\n## Limitations\n- Only works for the windows drives, (paths living in the wsl\'s `\'/mnt/\'` mount point) so `\'/home/\'` won\'t work for example.\n\n## Installation\n\n```bash\npip install wsl-pathlib\n```\n\n\n## Usage\n\n```python\nfrom wsl_pathlib.path import WslPath\n\n# Running on WSL\nwsl_p = WslPath("C:\\\\foo")\nprint(wsl_p)\n# => \'/mnt/c/foo\'\nprint(wsl_p.exists())\n# => True\nprint(wsl_p.win_path)\n# => \'C:\\foo\'\n\nwsl_p2 = wsl_p / "file.txt"\nprint(wsl_p2.win_path)\n# => \'C:\\foo\\file.txt\'\n```\n\n## License\n\n[MIT](https://github.com/psychonaute/wsl-pathlib/blob/master/LICENSE)\n\n\n## Credits\n\nThis project was generated with [`wemake-python-package`](https://github.com/wemake-services/wemake-python-package). Current template version is: [465848d4daab031f9be6e334ef34af011c2577bc](https://github.com/wemake-services/wemake-python-package/tree/465848d4daab031f9be6e334ef34af011c2577bc). See what is [updated](https://github.com/wemake-services/wemake-python-package/compare/465848d4daab031f9be6e334ef34af011c2577bc...master) since then.\n',
    'author': None,
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/psychonaute/wsl-pathlib',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
