"""Declares :class:`TrustStore`."""
import asyncio

import ioc.loader

from .abstractkeystore import AbstractKeystore


class TrustStore(AbstractKeystore):
    """Like :class:`~unimatrix.ext.crypto.AbstractKeystore`, but only
    works with public keys.
    """
    __module__ = 'unimatrix.ext.crypto'

    async def jwks(self, url: str, tags: list, annotations: dict) -> None:
        """Import keys from the JWKS served from `url`."""
        cls = ioc.loader.import_symbol(
            "unimatrix.ext.crypto.loaders.WellKnownOAuthLoader"
        )
        loader = cls(tags=tags, annotations=annotations, opts={'server': url})
        return await self.run_loader(loader)

    async def load(self, loaders):
        """Loads public keys using the given `loaders`."""
        loaders = [
            ioc.loader.import_symbol(x.pop('loader'))(**x)
            for x in loaders
        ]
        await asyncio.gather(*map(self.run_loader, loaders))

    async def run_loader(self, loader):
        """Runs given `loader` and imports its keys into the
        trust store.
        """
        keys = []
        async for key in loader.import_keys():
            self.register(key)
            keys.append(key)
        return keys


trust = TrustStore()
