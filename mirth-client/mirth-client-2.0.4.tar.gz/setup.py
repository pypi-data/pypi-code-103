# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['mirth_client']

package_data = \
{'': ['*']}

install_requires = \
['httpx>=0.18,<0.22',
 'pydantic>=1.8.2,<2.0.0',
 'semver>=2.13.0,<3.0.0',
 'typing-extensions>=3.10.0,<4.0.0',
 'xmltodict>=0.12.0,<0.13.0']

extras_require = \
{'docs': ['Sphinx>=3.5.3,<5.0.0', 'sphinx-rtd-theme>=0.5.1,<1.1.0']}

setup_kwargs = {
    'name': 'mirth-client',
    'version': '2.0.4',
    'description': 'Basic Python interface for Mirth Connect',
    'long_description': '# python-mirth-client\n\n[![PyPI Release](https://img.shields.io/pypi/v/mirth-client)](https://pypi.org/project/mirth-client/)\n[![Documentation Status](https://readthedocs.org/projects/python-mirth-client/badge/?version=latest)](https://python-mirth-client.readthedocs.io/en/latest/?badge=latest)\n\nA basic async Python interface for Mirth Connect\n\n## Installation\n\n`pip install mirth-client`\n\n## Usage example\n\nAssuming running within IPython or as part of an async application with an event-loop set up.\n\n```python\nfrom mirth_client import MirthAPI\nfrom pprint import pprint\n\nasync with MirthAPI("https://mirth.domain.com/api") as api:\n    await api.login("****", "****")\n\n    # Check out list of channels\n    for channel in await api.get_channels():\n        metadata = await channel.get()\n        print(f"ID: {metadata.id}")\n        print(f"Name: {metadata.name}")\n        print("")\n\n    # Get stats for a channel\n    s = await channels["3cdefad2-bf10-49ee-81c9-8ac6fd2fed67"].get_statistics()\n    pprint(s)\n\n    # Check channel for failed messages\n    e = await channels["3cdefad2-bf10-49ee-81c9-8ac6fd2fed67"].get_messages(status="error")\n    pprint(e)\n\n    # Get 10 most recent events\n    e = await api.get_events(10)\n    pprint(e)\n```\n',
    'author': 'Joel Collins',
    'author_email': 'joel.collins@renalregistry.nhs.uk',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.6.2,<4.0.0',
}


setup(**setup_kwargs)
