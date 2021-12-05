import multiprocessing
import os
import typing
from collections import OrderedDict

import geopandas as gp
import pandas as pd
from shapely.geometry import Point

import sys
import logging

logging.basicConfig(
    format='%(asctime)s [%(levelname)s] %(name)s - %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S',
    stream=sys.stdout,
)


def geometry_point(lat_lon):
    if lat_lon and not pd.isna(lat_lon):
        x, y = float(lat_lon.get('longitude')), float(lat_lon.get('latitude'))
        return Point(x, y)
    return Point()


def set_index_column(df, col_name):
    index_column = df.pop(col_name)

    df.insert(0, col_name, index_column)
    return df.set_index(col_name)


def tz_naive(d):
    return d.tzinfo is None or d.tzinfo.utcoffset(d) is None


def export(df, filename='ouput.csv', layer=None, mode='w', **kwargs):
    if isinstance(df, pd.DataFrame) and filename.endswith('.csv'):
        df.to_csv(filename)
    # writing to spatial data.
    elif isinstance(df, gp.GeoDataFrame):
        if filename.endswith('.shp'):
            df.to_file(filename, mode=mode)
        elif filename.endswith('.gpkg'):
            df.to_file(filename, driver='GPKG', layer=layer)
    else:
        df.to_file(filename)


def parallelize_df(df: typing.Iterable, func: typing.Callable, processes: int = 10):
    """
    Using pool of worker processes to offload tasks
    # https://docs.python.org/3/library/multiprocessing.html#using-a-pool-of-workers
    """
    processes = processes or os.cpu_count()
    with multiprocessing.pool.Pool(processes) as p:
        df = pd.concat(p.map(func, df))
    df.reset_index(inplace=True, drop=True)
    return df


def normalize_dict(x, colname=None):
    """normalize dict into individual columns"""
    try:
        _x = x.get(colname)
        index = list(x.index)
        if _x:
            _x = OrderedDict(x[colname])
        else:
            _x = OrderedDict()
        for key in _x.keys():
            if key not in index:
                x[str(key)] = _x.get(key)
            else:
                x['_'.join((colname, str(key)))] = _x.get(key)
        x = x.drop(colname)
    except Exception as e:
        print(str(e))
    finally:
        return x


def flatten_dict(x, colname=None):
    """normalize dict into individual columns"""
    try:
        _y = x.get(colname)
        _x = None
        if (_y is not None) and (_y != ''):
            _x = OrderedDict(x[colname])
        else:
            _x = OrderedDict()
        for key in _x.keys():
            x['_'.join((colname, str(key)))] = _x.get(key)
        x = x.drop(colname)
    except Exception as e:
        print(str(e))
    finally:
        return x


def memorize(func):
    cache = {}

    def wrapper(*args):
        if args in cache:
            return cache[args]
        result = func(*args)
        cache[args] = func(*args)
        return result
    return wrapper
