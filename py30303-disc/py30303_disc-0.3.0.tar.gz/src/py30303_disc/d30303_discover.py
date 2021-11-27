"""
Simple 30303 discover.

USAGE:
    d30303_discover
"""

import asyncio
import logging

from .libs.py30303_disc import d30303, run_d30303_discovery


async def main(loop):
    """Run the discovery."""
    logging.basicConfig(level=logging.DEBUG)

    d30303_discovery = d30303()
    d30303_discovery.bind_d30303_recv(loop=loop, d_type="ecowitt")

    scanner = run_d30303_discovery(server=d30303_discovery, loop=loop, d_type="ecowitt")

    found_dev = await scanner.get_found_devices()
    print(found_dev)
    loop.stop()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(loop))
    loop.run_forever()
