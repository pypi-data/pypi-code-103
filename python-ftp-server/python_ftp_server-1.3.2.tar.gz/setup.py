# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['python_ftp_server']

package_data = \
{'': ['*']}

install_requires = \
['pyftpdlib>=1.5.6', 'pyopenssl>=21.0.0', 'requests>=2.26']

extras_require = \
{':platform_system != "Windows"': ['pysendfile>=2.0.1']}

setup_kwargs = {
    'name': 'python-ftp-server',
    'version': '1.3.2',
    'description': 'Command line FTP server tool designed for performance and ease of use.',
    'long_description': '# Simple FTP server\n## Usage\n1. Configure firewall and ports forwarding (If you are behind NAT and OpenWRT is installed on your router, look at "./openwrt_firewall" and add it to the end of "/etc/config/firewall" on your router)\n2. Go to your directory that you want to share and run\n`./ftp_server.py`\n',
    'author': 'Vadym Stupakov',
    'author_email': 'vadim.stupakov@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/Red-Eyed/python_ftp_server',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.6,<=3.10',
}


setup(**setup_kwargs)
