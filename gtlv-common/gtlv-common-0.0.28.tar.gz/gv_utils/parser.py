#!/usr/bin/env python3

import asyncio
import io
import json
import os
from typing import Any, Callable, Generator

import numpy as np
import pandas as pd
from pandas.api import types as pdtypes
from shapely.geometry.base import BaseGeometry

from gv_utils.datetime import datetime, from_timestamp, to_timestamp
from gv_utils.enums import AttId, Message, MessageData, MessageKind
from gv_utils.geometry import decode_geometry, encode_geometry


class MessageEncoder(json.JSONEncoder):
    def default(self, o: Any) -> Any:
        if isinstance(o, datetime):
            return to_timestamp(o)
        elif isinstance(o, BaseGeometry):
            return encode_geometry(o)
        elif isinstance(o, pd.DataFrame):
            return encode_pandas(o)
        else:
            return super().default(o)


def encode_pandas(dataframe: pd.DataFrame) -> str:
    dataframe.fillna(MessageData.nan, inplace=True)
    for col in dataframe.columns:
        try:
            if pdtypes.is_numeric_dtype(dataframe[col]):
                dataframe[col] = dataframe[col]
        except:
            pass
    dataframe.replace(MessageData.nan, '', inplace=True)
    return dataframe.to_csv(sep=MessageData.csvseparator, quotechar=MessageData.csvquote)


async def encode_message(message: Any) -> str:
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, sync_encode_message, message)


def sync_encode_message(message: Any) -> str:
    return json.dumps(message, cls=MessageEncoder)


def add_main_prefix(messagekind: str) -> str:
    return '{prefix}{sep}{kind}'.format(prefix=MessageKind.mainprefix, sep=MessageKind.separator, kind=messagekind)


def object_hook(obj: dict, custom_data_decoder: Callable = None) -> dict:
    for key in obj:
        val = None
        if key == Message.timestamp:
            val = from_timestamp(obj[key])
        elif key == Message.data:
            if isinstance(obj[key], str):
                if custom_data_decoder is None:
                    custom_data_decoder = decode_pandas
            if custom_data_decoder is not None:
                try:
                    val = custom_data_decoder(obj[key])
                except:
                    pass
        elif key == AttId.geom:
            val = decode_geometry(obj[key])
        if val is not None:
            obj[key] = val
    return obj


async def decode_message(message: str, custom_data_decoder: Callable = None) -> dict:
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, sync_decode_message, message, custom_data_decoder)


def sync_decode_message(message: str, custom_data_decoder: Callable = None) -> dict:
    return json.loads(message, object_hook=lambda o: object_hook(o, custom_data_decoder))


def decode_pandas(data: str) -> pd.DataFrame:
    dataframe = pd.read_csv(io.StringIO(data), sep=MessageData.csvseparator, index_col=0)
    dataframe.replace(MessageData.nan, np.NaN, inplace=True)
    dataframe.replace(str(MessageData.nan), np.NaN, inplace=True)
    dataframe.dropna(inplace=True)
    try:
        dataframe.index = dataframe.index.astype('str')
    except:
        pass
    return dataframe


def get_dataframe_timestamp(df: pd.DataFrame) -> int:
    return int(df.index.name)
