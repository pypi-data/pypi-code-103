# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['solana',
 'solana._layouts',
 'solana.rpc',
 'solana.rpc._utils',
 'solana.rpc.providers',
 'solana.utils',
 'spl',
 'spl.token']

package_data = \
{'': ['*']}

install_requires = \
['PyNaCl>=1.4.0,<2.0.0',
 'apischema>=0.16.1,<0.17.0',
 'base58>=2.0.1,<3.0.0',
 'cachetools>=4.2.2,<5.0.0',
 'construct-typing>=0.5.2,<0.6.0',
 'httpx>=0.18.2,<0.19.0',
 'jsonrpcclient>=4.0.1,<5.0.0',
 'jsonrpcserver>=5.0.4,<6.0.0',
 'requests>=2.24,<3.0',
 'types-cachetools>=4.2.4,<5.0.0',
 'typing-extensions>=3.10.0,<4.0.0',
 'websockets>=10.1,<11.0']

setup_kwargs = {
    'name': 'solana',
    'version': '0.19.0',
    'description': 'Solana Python API',
    'long_description': '[![Actions\nStatus](https://github.com/michaelhly/solanapy/workflows/CI/badge.svg)](https://github.com/michaelhly/solanapy/actions?query=workflow%3ACI)\n[![PyPI version](https://badge.fury.io/py/solana.svg)](https://badge.fury.io/py/solana)\n[![PyPI pyversions](https://img.shields.io/pypi/pyversions/solana)](https://pypi.org/project/solana/)\n[![Codecov](https://codecov.io/gh/michaelhly/solana-py/branch/master/graph/badge.svg)](https://codecov.io/gh/michaelhly/solana-py/branch/master)\n[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://github.com/michaelhly/solana-py/blob/master/LICENSE)\n[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)\n\n# Solana.py\n\nSolana Python API built on the [JSON RPC API](https://docs.solana.com/apps/jsonrpc-api).\n\nPython version of [solana-web3.js](https://github.com/solana-labs/solana-web3.js/) for interacting with Solana.\n\nRead the [Documentation](https://michaelhly.github.io/solana-py/).\n\nAlso check out [anchorpy](https://kevinheavey.github.io/anchorpy/), a Python client for\n[Anchor](https://project-serum.github.io/anchor/getting-started/introduction.html) based programs on Solana.\n\n## Quickstart\n\n### Installation\n\n```sh\npip install solana\n```\n\n### General Usage\n\n```py\nimport solana\n```\n\n### API Client\n\n```py\nfrom solana.rpc.api import Client\n\nhttp_client = Client("https://api.devnet.solana.com")\n```\n\n### Async API Client\n\n```py\nimport asyncio\nfrom solana.rpc.async_api import AsyncClient\n\nasync def main():\n    async with AsyncClient("https://api.devnet.solana.com") as client:\n        res = await client.is_connected()\n    print(res)  # True\n\n    # Alternatively, close the client explicitly instead of using a context manager:\n    client = AsyncClient("https://api.devnet.solana.com")\n    res = await client.is_connected()\n    print(res)  # True\n    await client.close()\n\nasyncio.run(main())\n```\n\n### Websockets Client\n\n```py\n    import asyncio\n    from asyncstdlib import enumerate\n    from solana.rpc.websocket_api import connect\n\n    async def main():\n        async with connect("ws://api.devnet.solana.com") as websocket:\n            await websocket.logs_subscribe()\n            first_resp = await websocket.recv()\n            subscription_id = first_resp.result\n            next_resp = await websocket.recv()\n            print(next_resp)\n            await websocket.logs_unsubscribe(subscription_id)\n\n        # Alternatively, use the client as an infinite asynchronous iterator:\n        async with connect("ws://api.devnet.solana.com") as websocket:\n            await websocket.logs_subscribe()\n            first_resp = await websocket.recv()\n            subscription_id = first_resp.result\n            async for idx, msg in enumerate(websocket):\n                if idx == 3:\n                    break\n                print(msg)\n            await websocket.logs_unsubscribe(subscription_id)\n\n    asyncio.run(main())\n```\n\n## Development\n\n### Setup\n\n1. Install [poetry](https://python-poetry.org/docs/#installation)\n2. Install dev dependencies:\n```sh\npoetry install\n\n```\n\n3. Activate the poetry shell.\n\n```sh\npoetry shell\n```\n\n### Lint\n\n```sh\nmake lint\n```\n\n### Tests\n\n```sh\n# All tests\nmake tests\n# Unit tests only\nmake unit-tests\n# Integration tests only\nmake int-tests\n```\n\n### Start a Solana Localnet\n\nInstall [docker](https://docs.docker.com/get-started/).\n\n```sh\n# Update/pull latest docker image\nmake update-localnet\n# Start localnet instance\nmake start-localnet\n```\n',
    'author': 'Michael Huang',
    'author_email': 'michaelhly@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/michaelhly/solanapy',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
