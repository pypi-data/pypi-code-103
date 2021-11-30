import asyncio
import aioredis
import platform

if not (platform.system() == 'Windows'):
    import uvloop

    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())  # 使用 uvloop 来替换 asyncio 内部的事件循环。


class GeneralAsyncIoRedis:
    def __init__(self, *args, **kwargs):
        super(GeneralAsyncIoRedis, self).__init__(*args, **kwargs)

    async def get_async_redis_conn(self, **kwargs):
        return await aioredis.create_redis_pool((kwargs.get('redis_host'), kwargs.get('redis_port')), encoding='utf-8',
                                                db=kwargs.get('redis_db'), password=kwargs.get('redis_pwd'),
                                                loop=asyncio.get_event_loop())

    async def aio_redis_conn_close(self):
        if self.aio_redis_conn:
            self.aio_redis_conn.close()
            await self.aio_redis_conn.wait_closed()

# async def test():
#     redis = GeneralAsyncIoRedis()
#     r = await redis.get_redis_pool()
#     await redis.set('my-key', 'value')
#     value = await redis.get('my-key', encoding='utf-8')
#     await redis.close()
