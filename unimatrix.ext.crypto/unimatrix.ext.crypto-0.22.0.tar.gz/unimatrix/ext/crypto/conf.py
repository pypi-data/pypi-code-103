"""Provides the interface to configure the :mod:`unimatrix.ext.crypto`
package at runtime.
"""
import asyncio
import concurrent.futures

import ioc.loader
import unimatrix.lib.etc
from unimatrix.lib import meta
from unimatrix.lib.datastructures import ImmutableDTO

from .keychain import chain


@meta.allow_sync
async def configure(**config):
    """Configure the :mod:`unimatrix.ext.crypto` package."""
    config = ImmutableDTO.fromdict(config)

    # Run all loaders if they are configured.
    futures = []
    for loader_config in (config.get('loaders') or []):
        Loader = ioc.loader.import_symbol(loader_config.loader)
        instance = Loader(
            loader_config.options,
            public_only=loader_config.get('public_only', False)
        )
        futures.append(instance.load())

    if futures:
        await asyncio.gather(*futures)


def load(config):
    """Load keys from a YAML configuration file or dictionary."""
    if isinstance(config, str):
        config = unimatrix.lib.etc.load(config)
    assert isinstance(config, dict) # nosec
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = []
        for k in config.get('keys') or {}:
            f = executor.submit(chain.register_deferred, {
                **config['keys'][k],
                'alias': k
            })
            futures.append(f)
        executor.shutdown(wait=True)
        [f.result() for x in futures]
