# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['aiovotifier']

package_data = \
{'': ['*']}

install_requires = \
['cryptography>=35.0.0,<36.0.0']

setup_kwargs = {
    'name': 'aiovotifier',
    'version': '1.0.5',
    'description': 'An asynchronous MInecraft server votifier client in Python',
    'long_description': '# Aio-Votifier ![Code Quality](https://www.codefactor.io/repository/github/iapetus-11/aio-votifier/badge) ![PYPI Version](https://img.shields.io/pypi/v/aiovotifier.svg) ![PYPI Downloads](https://img.shields.io/pypi/dw/aiovotifier?color=0FAE6E) ![Views](https://api.ghprofile.me/view?username=iapetus-11.aio-votifier&color=0FAE6E&label=views&style=flat)\n*An asynchronous MInecraft server votifier client in Python*\n\n## Example Usage:\n```py\nfrom aiovotifier import VotifierClient\nimport asyncio\n\nasync def main():\n    client = VotifierClient("127.0.0.1", 8192, "testservicename", "token/rsa key")\n    \n    # VotifierClient.vote(...) automatically determines the protocol and key format\n    await client.vote("username", "user address")\n    await client.vote("user2")\n\n    await client.v1_vote("username", "user address")  # only supports v1 protocol\n    await client.nu_vote("username", "user address")  # only supports NuVotifier/v2 protocol\n\nasyncio.run(main())\n```\n\n## Documentation\n#### *class* aiovotifier.**VotifierClient**(host: *str*, port: *int*, service_name: *str*, secret: *str*)\n- Arguments:\n    - `host: str` - *The hostname or IP of the votifier server*\n    - `port: int` - *The port of the votifier server, commonly 8192*\n    - `service_name: str` - *The name of the service that sends the vote*\n    - `secret: str` - *The public RSA key or the token found in `config.yml`*\n- Methods:\n    - `vote(username: str, user_address: str = "127.0.0.1")` - *sends a vote to the votifier server, automatically detects and handles the protocol and type of secret*\n    - `v1_vote(username: str, user_address: str = "127.0.0.1")` - *sends a Votifier v1 vote to a votifier v1 server*\n    - `nu_vote(username: str, user_address: str = "127.0.0.1") -> dict` - *sends a NuVotifier / v2 vote to a NuVotifier server, returns the response from the server*\n\n#### *class* aiovotifier.**VotifierHeader**(header: *bytes*, version: *str*, token: *str* = None)\n- Arguments:\n    - `header: bytes` - *The header received from the votifier server*\n    - `version: str` - *The version of the votifier server*\n    - `challenge: str = None` - *The challenge, included only if the votifier server is v2/NuVotifier*\n- Methods:\n    - `@classmethod parse(header: bytes)` - *Returns a new `VotifierHeader`, parsed from the input bytes*\n\n#### *function* aiovotifier.**votifier_v1_vote**(r: *asyncio.StreamReader*, w: *asyncio.StreamWriter*, service_name: *str*, username: *str*, user_address: *str*, key: *cryptography.hazmat.primitives.asymmetric.rsa.RSAPublicKey*)\n- *Sends a Votifier v1 vote to a Votifier v1 server*\n\n#### *function* aiovotifier.**nuvotifier_vote**(r: *asyncio.StreamReader*, w: *asyncio.StreamWriter*, service_name: *str*, username: *str*, user_address: *str*, token: *str*, challenge: *str*) -> *dict*\n- *Sends a NuVotifier / v2 vote to a NuVotifier server*\n\n#### *exception* aiovotifier.**VotifierError**\n- *Base class that all votifier exceptions derive from*\n\n#### *exception* aiovotifier.**VotifierHeaderError**\n- *Raised when the header from the votifier server is invalid*\n\n#### *exception* aiovotifier.**UnsupportedVersionError**\n- *Raised when the votifier version is unsupported*\n\n#### *exception* aiovotifier.**NuVotifierResponseError**\n- *Raised when the response from the votifier server contains a status that is not OK*\n\n## Credits\n*aiovotifier was based off the code and documentation below*\n- https://github.com/ano95/votifier2-py\n- https://www.npmjs.com/package/votifier-client/v/0.1.0?activeTab=dependents\n- https://github.com/vexsoftware/votifier\n- https://github.com/NuVotifier/NuVotifier/wiki/Technical-QA\n',
    'author': 'Milo Weinberg',
    'author_email': 'iapetus011@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
