# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['signalr_async',
 'signalr_async.net',
 'signalr_async.netcore',
 'signalr_async.netcore.protocols']

package_data = \
{'': ['*']}

install_requires = \
['aiohttp>=3.6.0,<4.0.0', 'msgpack>=1.0.2,<2.0.0']

setup_kwargs = {
    'name': 'signalr-async',
    'version': '2.3.0',
    'description': 'Python SignalR async client',
    'long_description': '# SignalR-Async\n\n<p align="center">\n<a href="https://app.travis-ci.com/sam-mosleh/signalr-async" target="_blank">\n    <img src="https://app.travis-ci.com/sam-mosleh/signalr-async.svg?branch=master" alt="Test">\n</a>\n\n<a href="https://codecov.io/gh/sam-mosleh/signalr-async">\n  <img src="https://codecov.io/gh/sam-mosleh/signalr-async/branch/master/graph/badge.svg?token=JYBKXSFAX6"/>\n</a>\n\n<a href="https://pypi.org/project/signalr-async/" target="_blank">\n    <img src="https://img.shields.io/pypi/v/signalr-async" alt="Package version">\n</a>\n<a href="https://pypi.org/project/signalr-async/" target="_blank">\n    <img src="https://img.shields.io/pypi/pyversions/signalr-async.svg" alt="Supported Python versions">\n</a>\n</p>\n\nSignalR-Async is a python client for ASP.NET & ASP.NET Core SignalR, ready for building bidirectional communication.\n\n## Installation\n\n```bash\npip install signalr-async\n```\n\n## Example\n\n### Create it\n\n* Create a file `main.py` with:\n\n```Python\nimport asyncio\nfrom signalr_async.netcore import Hub, Client\nfrom signalr_async.netcore.protocols import MessagePackProtocol\n\n\nclass MyHub(Hub):\n    async def on_connect(self, connection_id: str) -> None:\n        """Will be awaited after connection established"""\n\n    async def on_disconnect(self) -> None:\n        """Will be awaited after client disconnection"""\n\n    def on_event_one(self, x: bool, y: str) -> None:\n        """Invoked by server synchronously on (event_one)"""\n\n    async def on_event_two(self, x: bool, y: str) -> None:\n        """Invoked by server asynchronously on (event_two)"""\n\n    async def get_something(self) -> bool:\n        """Invoke (method) on server"""\n        return await self.invoke("method", "arg1", 2)\n\n\nhub = MyHub("my-hub")\n\n\n@hub.on("event_three")\nasync def three(z: int) -> None:\n    pass\n\n\n@hub.on\nasync def event_four(z: int) -> None:\n    pass\n\n\nasync def multi_event(z: int) -> None:\n    pass\n\n\nfor i in range(10):\n    hub.on(f"event_{i}", multi_event)\n\n\nasync def main():\n    token = "mytoken"\n    async with Client(\n        "https://localhost:9000",\n        hub,\n        connection_options={\n            "extra_headers": {"Authorization": f"Bearer {token}"},\n            "protocol": MessagePackProtocol(),\n        },\n    ) as client:\n        return await hub.get_something()\n\n\nasyncio.run(main())\n```\n\n## Resources\n\nSee the [SignalR Documentation](https://docs.microsoft.com/aspnet/core/signalr) at docs.microsoft.com for documentation on the latest release.\n',
    'author': 'Sam Mosleh',
    'author_email': 'sam.mosleh@ut.ac.ir',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/sam-mosleh/signalr-async',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
