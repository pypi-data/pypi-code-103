# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['zalando_cli_bundle']

package_data = \
{'': ['*']}

install_requires = \
['click>=7.0,<8.0',
 'stups-cli-support>=1.1.22,<2.0.0',
 'stups-kio>=0.1.25,<0.2.0',
 'stups-pierone>=1.1.47,<2.0.0',
 'stups-zign>=1.2,<2.0',
 'zalando-aws-cli>=1.2.7,<2.0.0',
 'zalando-kubectl>=1.19.6,<2.0.0']

entry_points = \
{'console_scripts': ['zalando-cli-bundle = zalando_cli_bundle:cli.main']}

setup_kwargs = {
    'name': 'zalando-cli-bundle',
    'version': '21.12.0',
    'description': 'CLI bundle for Zalando developers',
    'long_description': None,
    'author': 'Henning Jacobs',
    'author_email': 'henning@zalando.de',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.bus.zalan.do/developer-productivity/zalando-cli-bundle',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
