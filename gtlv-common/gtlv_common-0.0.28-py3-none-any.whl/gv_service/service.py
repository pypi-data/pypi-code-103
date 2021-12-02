#!/usr/bin/env python3

import asyncio
import os
import traceback
from typing import Any, Awaitable, Callable

from gv_pubsub.pubsub import PubSub
from gv_requests.requests import Requests
from gv_utils.asyncio import check_event_loop
from gv_utils.datetime import datetime
from gv_utils.enums import MessageKind
from gv_utils.geometry import BaseGeometry
from gv_utils.logger import Logger


class Service:
    samplings = {MessageKind.karrusrd: 1 * 60, MessageKind.metropme: 1 * 60, MessageKind.tomtomfcd: 1 * 60}

    def __init__(self, logger: Logger, futures: list = None, callbacks: dict = None,
                 custom_data_decoder: Callable = None, offlineprefix: str = None) -> None:
        if futures is None:
            futures = []
        if callbacks is None:
            callbacks = {}
        if offlineprefix is None:
            offlineprefix = 'OFFLINE'

        self.logger = logger
        self.futures = futures
        self.callbacks = callbacks
        self.pubsub = PubSub(self.logger, custom_data_decoder)
        self.requests = Requests(logger)
        self.offlineprefix = offlineprefix
        self._mainfut = None

    async def async_init(self) -> None:
        pass

    def start(self, redisaddr: str, apiaddr: str) -> None:
        check_event_loop()  # will create a new event loop if needed (if we are not in the main thread)
        self.logger.info('Service is starting...')
        try:
            asyncio.run(self._run(redisaddr, apiaddr))
        except KeyboardInterrupt:
            pass
        self.logger.info('Service has stopped.')

    async def _run(self, redisaddr: str, apiaddr: str) -> None:
        try:
            await asyncio.gather(self.pubsub.async_init(redisaddr), self.requests.async_init(apiaddr))
            await self.async_init()
            self.logger.info('Service has started.')
            try:
                self._mainfut = asyncio.gather(
                    *self.futures,
                    *[self._subscribe(datakind, callback) for datakind, callback in self.callbacks.items()]
                )
                await self._mainfut
            except (KeyboardInterrupt, asyncio.CancelledError):
                self._cancel()
            except:
                self.logger.error('An error occurred in the main task. Exiting!{}{}'.format(os.linesep,
                                                                                            traceback.format_exc()))
            finally:
                await self._close()
        except:
            self.logger.error('An error occurred at init. Exiting!{}{}'.format(os.linesep,
                                                                               traceback.format_exc()))
            await self._close()

    async def _close(self) -> None:
        await asyncio.gather(self.pubsub.close(), self.requests.close())

    def _cancel(self) -> None:
        if self._mainfut is not None:
            self._mainfut.cancel()
            self._mainfut = None

    async def _publish(self, data: object, dataformat: str, datatimestamp, datakind: str) -> bool:
        return await self.pubsub.publish(data, dataformat, datatimestamp, datakind)

    async def _subscribe(self, datakind: str, callback: Callable[[dict], Awaitable]) -> None:
        await self.pubsub.subscribe(datakind, callback)

    async def _get_data_point(self, datapointeids: list = None, datatypeeids: list = None,
                              area: BaseGeometry = None) -> list:
        return await self.requests.get_data_point(datapointeids, datatypeeids, area)

    async def _get_road(self, roadeids: list = None, area: BaseGeometry = None) -> list:
        return await self.requests.get_road(roadeids, area)

    async def _get_road_center(self, roadeids: list = None, area: BaseGeometry = None) -> list:
        return await self.requests.get_road_center(roadeids, area)

    async def _get_turn_ratio(self, fromroad: str = None, toroad: str = None) -> list:
        return await self.requests.get_turn_ratio(fromroad, toroad)

    async def _get_prediction_point(self) -> list:
        return await self.requests.get_prediction_point()

    async def _get_zone_point(self, zoneeids: list = None, area: BaseGeometry = None) -> list:
        return await self.requests.get_zone_point(zoneeids, area)

    async def _get_road_data_point(self, datatype: str = None, area: BaseGeometry = None) -> list:
        return await self.requests.get_road_data_point(datatype, area)

    async def _get_data_point_data_quality(self, fromdatetime: datetime, todatetime: datetime = None,
                                           datapointeids: list = None, datatypeeids: list = None, period: str = None,
                                           sampling: str = None, window: str = None) -> dict:
        return await self.requests.get_data_point_data_quality(fromdatetime, todatetime, datapointeids, datatypeeids,
                                                               period, sampling, window)

    async def _get_data_type_data_quality(self, fromdatetime: datetime, todatetime: datetime = None,
                                          datatypeeids: list = None, period: str = None, sampling: str = None,
                                          window: str = None) -> dict:
        return await self.requests.get_data_type_data_quality(fromdatetime, todatetime, datatypeeids, period, sampling,
                                                              window)

    async def _get_road_data_quality(self, fromdatetime: datetime, todatetime: datetime = None, roadeids: list = None,
                                     period: str = None, sampling: str = None, window: str = None) -> dict:
        return await self.requests.get_road_data_quality(fromdatetime, todatetime, roadeids, period, sampling, window)

    async def _get_data_point_indicator(self, indicator: str, fromdatetime: datetime, todatetime: datetime = None,
                                        datapointeids: list = None, datatypeeids: list = None, period: str = None,
                                        sampling: str = None, window: str = None) -> dict:
        return await self.requests.get_data_point_indicator(indicator, fromdatetime, todatetime, datapointeids,
                                                            datatypeeids, period, sampling, window)

    async def _get_road_indicator(self, indicator: str, fromdatetime: datetime, todatetime: datetime = None,
                                  roadeids: list = None, period: str = None, sampling: str = None,
                                  window: str = None) -> dict:
        return await self.requests.get_road_indicator(indicator, fromdatetime, todatetime, roadeids, period, sampling,
                                                      window)

    async def _get_zone_travel_time(self, fromdatetime: datetime, todatetime: datetime = None, period: str = None,
                                    sampling: str = None, frompointeid: str = None, topointeid: str = None) -> dict:
        return await self.requests.get_zone_travel_time(fromdatetime, todatetime, period,
                                                        sampling, frompointeid, topointeid)

    @staticmethod
    async def _get_not_empty(get_func: Callable, args: tuple = (), kwargs: dict = None) -> Any:
        if kwargs is None:
            kwargs = {}

        res = {}
        while len(res) == 0:
            res = await get_func(*args, **kwargs)
        return res


def start(Application, threaded=False):
    if threaded:
        import threading
        threading.Thread(target=start, args=(Application, False), daemon=True).start()
        print('Starting application in a background thread...')
    else:
        Application()
