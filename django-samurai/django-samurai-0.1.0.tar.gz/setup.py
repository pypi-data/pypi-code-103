# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['samurai']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'django-samurai',
    'version': '0.1.0',
    'description': '?',
    'long_description': '# django-samurai\n🤫\n\n`poetry build -f sdist`\n`poetry publish`\n',
    'author': 'c4ffein',
    'author_email': 'c4ffein.work@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
