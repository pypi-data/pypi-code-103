# -*- coding: utf-8 -*-
from setuptools import setup

modules = \
['main']
entry_points = \
{'console_scripts': ['md5-brute-force = main:entrypoint']}

setup_kwargs = {
    'name': 'md5-brute-force',
    'version': '1.0.0',
    'description': 'Python script for brute forcing an md5 hash.',
    'long_description': '# Script to brute force an md5 hash.\n\n![md5-brute-force](https://github.com/vsevolod-mineev/md5-brute-force/blob/main/images/md5-brute-force.gif?raw=true)\n\nThis script is for brute forcing your way through an md5 hash. Install the package using `pip install`, run the script, paste your hash -> done.\n\n# How to use:\nTo install `md5-brute-force` using `pip install`:\n```\npip install md5-brute-force\n```\n\nTo execute the script enter:\n```\nmd5-brute-force\n```\n',
    'author': 'Vsevolod Mineev',
    'author_email': 'vsevolod.mineev@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/vsevolod-mineev/md5-brute-force',
    'py_modules': modules,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<3.11',
}


setup(**setup_kwargs)
