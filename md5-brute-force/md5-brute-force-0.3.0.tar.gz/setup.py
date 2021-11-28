# -*- coding: utf-8 -*-
from setuptools import setup

modules = \
['main']
setup_kwargs = {
    'name': 'md5-brute-force',
    'version': '0.3.0',
    'description': 'Python script for brute forcing an md5 hash.',
    'long_description': '# Script to brute force an md5 hash.\n\nThis script is for brute forcing your way through an md5 hash. Clone the repo, install the dependencies, run the script, paste your hash -> done.\n\n# How to use:\nIn order to use this script you must first install `poetry`.\n\nTo install `poetry` on osx or linux use:\n```\ncurl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python -\n```\nTo install `poetry` on windows powershell use:\n```\n(Invoke-WebRequest -Uri https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py -UseBasicParsing).Content | python -\n```\nClone this Github repository into your current directory before changing into it:\n```\ngit clone https://github.com/vsevolod-mineev/md5-bruteforce\n```\n```\ncd md5-bruteforce/\n```\nTo install the defined dependencies for this project use:\n```\npoetry install\n```\nTo execute the command within the virtual environment use:\n```\npoetry run\n```\n\nRun the script using the following format:\n```\npoetry run python3 main.py\n```\n\n# How does it work?\n![md5-brute-force](./images/md5-brute-force-image.png)\n\n',
    'author': 'Vsevolod Mineev',
    'author_email': 'vsevolod.mineev@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/vsevolod-mineev/md5-brute-force',
    'py_modules': modules,
    'python_requires': '>=3.9,<3.11',
}


setup(**setup_kwargs)
