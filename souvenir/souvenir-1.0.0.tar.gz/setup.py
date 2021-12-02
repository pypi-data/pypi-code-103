# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['souvenir']

package_data = \
{'': ['*']}

install_requires = \
['PyYAML>=6.0,<7.0', 'tabulate>=0.8.9,<0.9.0', 'typer>=0.4.0,<0.5.0']

entry_points = \
{'console_scripts': ['sv = souvenir.__main__:sv']}

setup_kwargs = {
    'name': 'souvenir',
    'version': '1.0.0',
    'description': 'Little CLI program which helps creating and viewing flashcards',
    'long_description': '# Souvenir\n\n> Little CLI program which helps creating and viewing flashcards\n\n## Usage\n\n```sh\n$ cat words.yml\n\n- fr: souvenir\n  en: to remember\n  ru: помнить\n\n- fr: parler\n  en: to speak\n  ru: говорить\n```\n\n```sh\n$ sv list words\n+----------+-------------+----------+\n| fr       | en          | ru       |\n|----------+-------------+----------|\n| souvenir | to remember | помнить  |\n| parler   | to speak    | говорить |\n+----------+-------------+----------+\n```\n\n```sh\n$ sv repeat words fr\n=> souvenir\n   en: to remember\n   ru: помнить\n=| correct? [y/n]\n\n=> parler\n   en: to speak\n   ru: говорить\n=| correct? [y/n]\n```\n',
    'author': 'Denis Gruzdev',
    'author_email': 'codingjerk@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/codingjerk/souvenir',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
