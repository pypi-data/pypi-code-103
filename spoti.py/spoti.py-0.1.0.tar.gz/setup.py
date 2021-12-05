# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['spotipy', 'spotipy.objects', 'spotipy.typings']

package_data = \
{'': ['*']}

modules = \
['py']
install_requires = \
['aiohttp>=3.6.0']

extras_require = \
{'speed': ['orjson>=3.5.4,<4.0.0']}

setup_kwargs = {
    'name': 'spoti.py',
    'version': '0.1.0',
    'description': 'An async Spotify Web API wrapper.',
    'long_description': '# spoti.py\nAn async wrapper for the [Spotify API](https://developer.spotify.com/documentation/web-api/) written in Python.\n\n## Support\nSupport for spoti.py can be found in my [Discord](https://discord.com/invite/w9f6NkQbde) or by opening a discussion/issue on the [GitHub repo](https://github.com/Axelancerr/spoti.py)\n\n## Installation\n\nspoti.py is not available on PyPi yet, but it can be installed from GitHub instead:\n```shell\npip install -U git+https://github.com/Axelancerr/spoti.py\n```\n\nTo add spoti.py to a `requirements.txt` file, you can simply add it as: \n```text\ngit+https://github.com/Axelancerr/spoti.py\n```\n',
    'author': 'Axel',
    'author_email': 'axelancerr@gmail.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://github.com/Axelware/spoti.py',
    'packages': packages,
    'package_data': package_data,
    'py_modules': modules,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.10.0,<4.0',
}


setup(**setup_kwargs)
