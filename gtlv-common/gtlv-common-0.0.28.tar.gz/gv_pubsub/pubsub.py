#!/usr/bin/env python3

import asyncio
import traceback
from typing import Awaitable, Callable

import aioredis

from gv_utils import parser
from gv_utils.enums import Message
from gv_utils.logger import Logger


class PubSub:

    def __init__(self, logger: Logger, custom_data_decoder: Callable = None) -> None:
        self.logger = logger
        self.redis = None
        self.custom_data_decoder = custom_data_decoder

    async def async_init(self, redisaddr: str) -> None:
        self.redis = await aioredis.create_redis_pool(redisaddr)

    async def publish(self, data: object, dataformat: str, datatimestamp, datakind: str) -> bool:
        success = False
        try:
            message = {
                Message.data: data,
                Message.format: dataformat,
                Message.timestamp: datatimestamp,
                Message.kind: datakind
            }
            await self.redis.publish(parser.add_main_prefix(datakind), await parser.encode_message(message))
            success = True
        except:
            self.logger.error(traceback.format_exc())
            self.logger.error('An error occurred while publishing {}.'.format(datakind))
        finally:
            return success

    async def subscribe(self, datakind: str, callback: Callable[[dict], Awaitable]) -> None:
        channel, = await self.redis.psubscribe(parser.add_main_prefix(datakind))
        self.logger.info('Service has subscribed to {}.'.format(datakind))
        while await channel.wait_message():
            try:
                _, message = await channel.get(encoding='utf-8')
                asyncio.create_task(callback(await parser.decode_message(message, self.custom_data_decoder)))
            except:
                self.logger.error(traceback.format_exc())
                self.logger.error('An error occurred while handling {}.'.format(datakind))
        self.logger.info('Service has unsubscribed from {}.'.format(datakind))

    async def close(self) -> None:
        if self.redis is not None:
            self.redis.close()
            await self.redis.wait_closed()
