# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['bauxite', 'bauxite.gateway', 'bauxite.http']

package_data = \
{'': ['*']}

install_requires = \
['aiohttp>=3.8.1,<4.0.0']

setup_kwargs = {
    'name': 'bauxite',
    'version': '1.0.0',
    'description': 'A robust, low-level connector for the Discord API',
    'long_description': '# Bauxite\n\nBauxite is a robus, low-level connector for the Discord API.\n\n## What is Bauxite for?\n\nBauxite is made for two main purposes:\n\n- Creating higher-level API wrappers and frameworks\n- Creating things that need high levels of control and low-level access to the Discord API\n\n## Examples\n\n### Basic HTTP Example\n\n```py\nfrom asyncio import run\n\nfrom bauxite import HTTPClient, Route\n\n\nasync def main() -> None:\n    client = HTTPClient("your_bot_token")\n\n    await client.request(\n        Route("POST", "/channels/{channel_id}/messages", channel_id=1234),\n        json={\n            "content": "Hello, world!",\n        },\n    )\n\n    await client.close()\n\nrun(main())\n```\n\n### Basic Gateway Example\n\n```py\nfrom asyncio import run\n\nfrom bauxite import GatewayClient, HTTPClient\n\n\nasync def callback(shard, direction, data) -> None:\n    print(f"{shard} [{direction}]: {data[\'op\'] or data[\'t\']}")\n\nasync def main() -> None:\n    client = HTTPClient("your_bot_token")\n    gateway = GatewayClient(client, 32767, callbacks=[callback])\n\n    await gateway.spawn_shards()\n\nrun(main())\n```\n',
    'author': 'vcokltfre',
    'author_email': 'vcokltfre@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/vcokltfre/bauxite',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
