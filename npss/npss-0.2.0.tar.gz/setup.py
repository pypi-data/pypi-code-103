# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['npss']

package_data = \
{'': ['*']}

entry_points = \
{'console_scripts': ['npss = npss:main']}

setup_kwargs = {
    'name': 'npss',
    'version': '0.2.0',
    'description': 'Your New Password!',
    'long_description': '![coverage](https://github.com/almazkun/npss/blob/main/.github/coverage.svg)\n\n# npss\nYour New Password!\n\n# Why?\nWhen need some password (token or random url safe string of specified length) quickly.\n\n# Perks:\nGenerate random string with specified length or length of 30 by default.\n* No dependencies.\n* Random.\n* Url safe.\n* At least one `-` included.\n\n# Installation:\n```bash\npip install npss\n```\n\n# Usage:\n```bash \nnpss\n```\n    >>>\n    J_9oE0uToBaw6qDzUAUI-hZ3PJC93B\n\n```bash \nnpss 255\n```\n    >>>\n    JwAiFQjuFizl6g1Thzx1AQdn39ozrPqsRJ4thyrs9OCjU28nUAx9k3fmB0jcSTtkZBVhF-DDV9-0zeod0OPN13k0gOEsA4FtSBtr6ckq81lQewOuLBUbFNUlKLH63Z6GSdZtuTidcQrvlVErnaY-pFb4xX8Jmj2jzJDpp6HvctEu5ycQq3VevlBwx9dIf8VUuO9jwZPsQnc022jbwBv00shByBOKCoO5I3TLGwnQEWaRHsWfyXeb6fTyzLtGH2-\n\n# Uninstall:\n```bash\npip uninstall npss\n```\n',
    'author': 'Almaz Kunpeissov',
    'author_email': 'hello@akun.dev',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/almazkun/npss',
    'packages': packages,
    'package_data': package_data,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
