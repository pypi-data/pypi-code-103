# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['python_ftp_server']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'python-ftp-server',
    'version': '1.3.5',
    'description': 'Command line FTP server tool designed for performance and ease of use.',
    'long_description': '# FTP server to transfer files between machines with zero configuration\n## Usage\n1. `python3 -m pip install python-ftp-server`\n2. `python3 -m python_ftp_server -d "dirctory/to/share"`\nwill print:\n```bash\nLocal address: ftp://<IP>:60000\nUser: <USER>\nPassword: <PASSWORD>\n```\n3. Copy and paste your `IP`, `USER`, `PASSWORD`, `PORT` into [FileZilla](https://filezilla-project.org/) (or any other FTP client):\n![img.png](img.png)\n',
    'author': 'Vadym Stupakov',
    'author_email': 'vadim.stupakov@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/Red-Eyed/python_ftp_server',
    'packages': packages,
    'package_data': package_data,
}


setup(**setup_kwargs)
