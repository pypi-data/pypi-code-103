import asyncio
from typing import Awaitable, Callable
from functools import wraps, partial


def sync_to_async(func: Callable) -> Awaitable:
    """将同步函数变为异步,使用方法:
    ```
    @sync_to_async
    def abc():
        print("success")

    async def cde():
        await abc()

    loop = asyncio.get_event_loop()
    loop.run_until_complete(asyncio.wait([cde()]))
    >>> success
    ```

    Args:
        func (Callable): 需要被装饰函数

    Returns:
        Awaitable: 异步函数
    """

    @wraps(func)
    async def run(*args, loop=None, executor=None, **kwargs):
        if loop is None:
            loop = asyncio.get_event_loop()
        pfunc = partial(func, *args, **kwargs)
        return await loop.run_in_executor(executor, pfunc)

    return run
