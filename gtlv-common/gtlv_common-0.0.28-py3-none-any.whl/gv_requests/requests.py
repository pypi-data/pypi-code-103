#!/usr/bin/env python3

from typing import Union

import aiohttp

from gv_utils import parser
from gv_utils.datetime import datetime, to_str
from gv_utils.enums import RequestParam, RequestPath
from gv_utils.geometry import BaseGeometry, encode_geometry
from gv_utils.logger import Logger

SEPARATOR = RequestPath.separator


class Requests:

    def __init__(self, logger: Logger) -> None:
        self.logger = logger
        self.apiurl = None

    async def async_init(self, apiaddr):
        self.apiurl = 'http://{}/api'.format(apiaddr)

    async def get_data_point(self, datapointeids: list = None, datatypeeids: list = None,
                             area: BaseGeometry = None) -> list:
        params = {}
        if datatypeeids is not None:
            params[RequestParam.datatype] = self.__encode_list_params(datatypeeids)
        return await self._get_location(datapointeids, area, RequestPath.datapoint, params)

    async def get_road(self, roadeids: list = None, area: BaseGeometry = None) -> list:
        return await self._get_location(roadeids, area, RequestPath.road)

    async def get_road_center(self, roadeids: list = None, area: BaseGeometry = None) -> list:
        return await self._get_location(roadeids, area, SEPARATOR.join((RequestPath.road, RequestPath.roadcenter)))

    async def get_turn_ratio(self, fromroad: str = None, toroad: str = None) -> list:
        params = {}
        if fromroad is not None:
            params[RequestParam.fromroad] = fromroad
        if toroad is not None:
            params[RequestParam.toroad] = toroad
        return await self._get(SEPARATOR.join((RequestPath.road, RequestPath.roadcenter, RequestPath.turnratio)),
                               params)

    async def get_prediction_point(self) -> list:
        return await self._get(RequestPath.predictionpoint)

    async def get_zone_point(self, zoneeids: list = None, area: BaseGeometry = None) -> list:
        return await self._get_location(zoneeids, area, RequestPath.zonepoint)

    async def _get_location(self, eids: list, area: BaseGeometry, applyto: str, params: dict = None) -> list:
        if params is None:
            params = {}

        if eids is not None:
            params[RequestParam.eid] = self.__encode_list_params(eids)
        if area is not None:
            params[RequestParam.within] = encode_geometry(area)
        return await self._get(applyto, params)

    async def get_road_data_point(self, datatype: str = None, area: BaseGeometry = None) -> list:
        params = {}
        if area is not None:
            params[RequestParam.within] = encode_geometry(area)
        if datatype is not None:
            params[RequestParam.datatype] = datatype
        return await self._get(SEPARATOR.join((RequestPath.road, RequestPath.datapoint)), params)

    async def get_data_point_data_quality(self, fromdatetime: datetime, todatetime: datetime = None,
                                          datapointeids: list = None, datatypeeids: list = None, period: str = None,
                                          sampling: str = None, window: str = None) -> dict:
        params = {}
        if datatypeeids is not None:
            params[RequestParam.datatype] = self.__encode_list_params(datatypeeids)
        return await self._get_data_quality(fromdatetime, todatetime, datapointeids, period, sampling, window,
                                            RequestPath.datapoint, params)

    async def get_data_type_data_quality(self, fromdatetime: datetime, todatetime: datetime = None,
                                         datatypeeids: list = None, period: str = None, sampling: str = None,
                                         window: str = None) -> dict:
        return await self._get_data_quality(fromdatetime, todatetime, datatypeeids, period, sampling, window,
                                            RequestPath.datatype)

    async def get_road_data_quality(self, fromdatetime: datetime, todatetime: datetime = None, roadeids: list = None,
                                    period: str = None, sampling: str = None, window: str = None) -> dict:
        return await self._get_data_quality(fromdatetime, todatetime, roadeids, period, sampling, window,
                                            RequestPath.road)

    async def _get_data_quality(self, fromdatetime: datetime, todatetime: datetime, locationeids: list,
                                period: str, sampling: str, window: str, applyto: str, params: dict = None) -> dict:
        return await self.__get_data(fromdatetime, todatetime, locationeids, period, sampling, window,
                                     SEPARATOR.join((applyto, RequestPath.dataquality)), params)

    async def get_data_point_indicator(self, indicator: str, fromdatetime: datetime,
                                       todatetime: datetime = None, datapointeids: list = None,
                                       datatypeeids: list = None, period: str = None, sampling: str = None,
                                       window: str = None) -> dict:
        params = {RequestParam.indicator: indicator}
        if datatypeeids is not None:
            params[RequestParam.datatype] = self.__encode_list_params(datatypeeids)
        return await self.__get_data(fromdatetime, todatetime, datapointeids, period, sampling, window,
                                     SEPARATOR.join((RequestPath.datapoint, RequestPath.indicator)), params)

    async def get_road_indicator(self, indicator: str, fromdatetime: datetime, todatetime: datetime,
                                 roadeids: list = None, period: str = None, sampling: str = None,
                                 window: str = None) -> dict:
        params = {RequestParam.indicator: indicator}
        return await self.__get_data(fromdatetime, todatetime, roadeids, period, sampling, window,
                                     SEPARATOR.join((RequestPath.road, RequestPath.indicator, indicator)), params)

    async def __get_data(self, fromdatetime: datetime, todatetime: datetime, locationeids: list, period: str,
                         sampling: str, window: str, applyto: str, params: dict) -> dict:
        if params is None:
            params = {}

        params[RequestParam.fromdatetime] = to_str(fromdatetime)
        if todatetime is not None:
            params[RequestParam.todatetime] = to_str(todatetime)
        if locationeids is not None:
            params[RequestParam.eid] = self.__encode_list_params(locationeids)
        if period is not None:
            params[RequestParam.period] = period
        if sampling is not None:
            params[RequestParam.sampling] = sampling
        if window is not None:
            params[RequestParam.window] = window
        return await self._get(applyto, params)

    async def get_zone_travel_time(self, fromdatetime: datetime, todatetime: datetime, period: str, sampling: str,
                                   frompointeid: str = None, topointeid: str = None) -> dict:
        params = {
            RequestParam.fromdatetime: to_str(fromdatetime)
        }
        if todatetime is not None:
            params[RequestParam.todatetime] = to_str(todatetime)
        if period is not None:
            params[RequestParam.period] = period
        if sampling is not None:
            params[RequestParam.sampling] = sampling
        if frompointeid is not None:
            params[RequestParam.frompoint] = frompointeid
        if topointeid is not None:
            params[RequestParam.topoint] = topointeid
        return await self._get(SEPARATOR.join((RequestPath.zonepoint, RequestPath.traveltime)), params)

    async def _get(self, suffix: str, params: dict = None) -> Union[list, dict]:
        if params is None:
            params = {}
        params[RequestParam.internalflag] = ''
        message = []
        async with aiohttp.ClientSession() as session:
            url = '{}{}'.format(SEPARATOR.join((self.apiurl, suffix)), SEPARATOR)
            async with session.get(url, params=params) as resp:
                if resp.status == 200:
                    message = await parser.decode_message(await resp.text())
        return message

    @staticmethod
    def __encode_list_params(params: list) -> str:
        return RequestParam.separator.join(params)

    async def close(self) -> None:
        pass
