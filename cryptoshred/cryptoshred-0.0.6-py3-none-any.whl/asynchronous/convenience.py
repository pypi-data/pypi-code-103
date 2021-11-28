import asyncio
from concurrent.futures import Executor
from typing import Any, List, Optional

import cryptoshred.convenience as convenience


from cryptoshred.backends import KeyBackend
from functools import partial


async def find_and_decrypt(
    *,
    key_backend: KeyBackend,
    x: Any,
    loop: Optional[asyncio.AbstractEventLoop] = None,
    executor: Optional[Executor] = None
) -> Any:
    if not loop:
        loop = asyncio.get_event_loop()

    func = partial(convenience.find_and_decrypt, key_backend=key_backend, x=x)

    return await loop.run_in_executor(
        executor=executor,
        func=func,
    )


async def find_and_decrypt_in_dict(
    *,
    input: List[Any],
    key_backend: KeyBackend,
    loop: Optional[asyncio.AbstractEventLoop] = None,
    executor: Optional[Executor] = None
) -> Any:
    if not loop:
        loop = asyncio.get_event_loop()

    func = partial(
        convenience.find_and_decrypt_in_dict, input=input, key_backend=key_backend
    )
    return await loop.run_in_executor(executor=executor, func=func)
