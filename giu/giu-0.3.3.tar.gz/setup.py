# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['giu']

package_data = \
{'': ['*']}

install_requires = \
['atoml>=1.1.0,<2.0.0',
 'click>=8.0.3,<9.0.0',
 'halo>=0.0.31,<0.0.32',
 'requests>=2.26.0,<3.0.0']

entry_points = \
{'console_scripts': ['giu = giu.cli:giu']}

setup_kwargs = {
    'name': 'giu',
    'version': '0.3.3',
    'description': 'Gandi LiveDNS Updater - Command line tool to keep your dynamic ip up to date',
    'long_description': "# GIU\nGandi LiveDNS Updater - Command line tool to keep your dynamic ip up to date.\n\n[![yriveiro](https://circleci.com/gh/yriveiro/giu.svg?style=svg)](https://circleci.com/gh/yriveiro/giu)\n\n[![Downloads/Week](https://static.pepy.tech/personalized-badge/giu?period=week&units=international_system&left_color=black&right_color=orange&left_text=Downloads/Week)](https://pepy.tech/project/giu) [![Downloadsi/Month](https://static.pepy.tech/personalized-badge/giu?period=month&units=international_system&left_color=black&right_color=orange&left_text=Downloads/Month)](https://pepy.tech/project/giu) [![Downloads](https://static.pepy.tech/personalized-badge/giu?period=total&units=international_system&left_color=black&right_color=orange&left_text=Downloads)](https://pepy.tech/project/giu)\n\n## Prequisites\n\n* A valid key fro Gandi LiveDNS API. Use https://account.gandi.net/en/users/USER/security\n(`USER` is your Gandi user account).\n* Python 3.\n\n## Installation\n\nThe recommended way to install this package is through [pip](https://pip.pypa.io/en/stable/).\n\n```shell\npip install --user giu\n```\n\n## Usage\n\nTo use `giu` you need to create a `config.toml` file to hold the minimal set of\nconfigurations.\n\n```toml\n[api]\nurl = 'https://dns.api.gandi.net/v5/livedns'\nkey = 'YOUR_KEY'\n\n[dns]\ndomain = 'example.com'\nrecords = [\n    {'type' = 'A', 'name' = '@', 'ttl' = 18000},\n    {'type' = 'A', 'name' = '*', 'ttl' = 1800},\n]\n\n[resolver]\nproviders = [\n    'http://ipecho.net/plain',\n    'https://ifconfig.me/ip',\n    'http://www.mon-ip.fr'\n]\n```\n\n### Docker Compose\nIn this example the config is in the current folder.\n\n```shell\ndocker-composer up -d\n```\n\nBy default the process will check your configuration every hour and update it if\nthe process detects a drift in the desired state.\n\n### One shot\nIn this example the config file was created on `$HOME/.giu/example.com.toml`.\n\n```shell\ngiu sync --conf $HOME/.giu/example.com.toml\n```\n\n### Cronjob\nIn this example the config file was created on `$HOME/.giu/example.com.toml`.\n\n```shell\n$ crontab -e\n* */2 * * * giu sync --conf $HOME/.giu/example.com.toml\n```\n\n### Docker\nIn this example a config file in the `$PWD` folder is mounted in `/app/conf` and\nthe command runs in `dry-run` mode.\n\n```shell\ndocker run -it --rm -v $PWD:/app/conf yriveiro/giu:dev giu sync --dry-run --config /app/conf/config.toml\n\n✔ Dynamic IP fetched.\nℹ Current dynamic IP: XXX.XXX.XX.XX.\nℹ Dry run mode on.\nℹ TTL for 'A' record '@' on config: 1800\n✔ 'A' record '@' for foo.bar from Gandi LiveDNS\nℹ IP for 'A' record '@' on Gandi LiveDNS: XXX.XXX.XXX.XXX\nℹ TTL for 'A' record '@' on Gandi LiveDNS: 18000\nℹ Update needed, dry run mode, no update done.\nℹ TTL for 'A' record '*' on config: 1800\n✔ 'A' record '*' for toranja.tech from Gandi LiveDNS\nℹ IP for 'A' record '*' on Gandi LiveDNS: XXX.XXX.XXX.XXX\nℹ TTL for 'A' record '*' on Gandi LiveDNS: 1800\nℹ Update needed, dry run mode, no update done.\n```\n\n`/app/conf` folder is not configurable once the Docker image has hardening\napplyed and that is the writable folder.\n\n## Improvements\n\nSome improvements that I have ff the top of my head:\n\n* `put` command to create entries like CNAMES and so on.\n* `delete` command to delete entries\n* `backup` command to do backups\n* ~~Docker Image to run giu with docker compose or as a Cronjob on Kubernetes.~~\n",
    'author': 'Yago Riveiro',
    'author_email': 'yago.riveiro@gmail.com',
    'maintainer': 'Yago Riveiro',
    'maintainer_email': 'yago.riveiro@gmail.com',
    'url': 'https://github.com/yriveiro/giu',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
