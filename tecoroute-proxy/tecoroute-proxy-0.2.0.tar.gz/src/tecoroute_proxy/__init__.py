"""TecoRoute Proxy.

Example of synchronous use:

.. code-block:: python

    from tecoroute_proxy import ProxyServer

    proxy = ProxyServer(port=8080)
    proxy.run()

Example of asynchronous use:

.. code-block:: python

    from asyncio import run

    from tecoroute_proxy import ProxyServer

    proxy = ProxyServer(port=8080)
    run(proxy.run_async())

Example of asynchronous server startup:

.. code-block:: python

    from asyncio import ensure_future, get_event_loop

    from tecoroute_proxy import ProxyServer

    async def main():
        proxy = ProxyServer(port=8080)
        await proxy.start()

    ensure_future(main())
    get_event_loop().run_forever()
"""
from ._cli import cli
from ._request import ProxyRequest
from ._server import ProxyServer

__all__ = ["ProxyServer", "ProxyRequest", "cli"]
