# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['SibylSystem', 'SibylSystem.types']

package_data = \
{'': ['*']}

install_requires = \
['httpx>=0.20.0,<0.21.0']

setup_kwargs = {
    'name': 'sibylsystem',
    'version': '0.0.13',
    'description': 'Python Wrapper for the Sibyl System Antispam API for telegram',
    'long_description': '# SibylSystem-Py\n\n>Python3 wrapper for the Sibyl System antispam API for telegram\n\n## Installation\n\n```\npip install sibylsystem\n```\n\n# Usage\n\n```py\n>>> from SibylSystem import PsychoPass\n>>> c = PsychoPass("your token")\n\n    SibylSystem-Py Copyright (C) 2021 Sayan Biswas, AnonyIndian, AliWoto\n    This program comes with ABSOLUTELY NO WARRANTY.\n    This is free software, and you are welcome to redistribute it\n    under certain conditions.\n\n>>> c.get_info(2037525377)\nBan(user_id=2037525377, banned=True, reason=\'Arcane\', message=\'\', ban_source_url=\'\', date=\'2021-10-30T18:47:00.004137+05:30\', banned_by=895373440, crime_coefficient=0)\n```\n\n# Docs ?\n\n**Open the source and read the docstrings**\n',
    'author': 'Sayan Biswas',
    'author_email': 'sayan@pokurt.me',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/AnimeKaizoku/SibylSystem-Py',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
