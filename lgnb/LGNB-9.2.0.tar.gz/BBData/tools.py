#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   tools.py    
@Contact :   wangcc@csc.com.cn
@License :   (C)Copyright 2017-2018, CSC

@Modify Time      @Author    @Version    @Desciption
------------      -------    --------    -----------
2021/10/14 16:55   wangcc     1.0         None
'''


import json
import pandas as pd
import numpy as np
import numba as nb
import shutil
from tqdm import tqdm
from pathlib import Path
from datetime import datetime


def bisect_right(a, x, lo=0, hi=None):
    """ Return the index where to insert item x in list a, assuming a is sorted. """

    if lo < 0:
        raise ValueError('lo must be non-negative')
    if hi is None:
        hi = len(a)
    while lo < hi:
        mid = (lo + hi) // 2
        if x < a[mid]:
            hi = mid
        else:
            lo = mid + 1
    return lo


def bisect_left(a, x, lo=0, hi=None):
    """ Return the index where to insert item x in list a, assuming a is sorted. """

    if lo < 0:
        raise ValueError('lo must be non-negative')
    if hi is None:
        hi = len(a)
    while lo < hi:
        mid = (lo + hi) // 2
        if a[mid] < x:
            lo = mid + 1
        else:
            hi = mid
    return lo


def to_intdate(dt: (str, pd.Timestamp)):
    if isinstance(dt, str):
        return int(dt.replace('-', ''))
    if isinstance(dt, pd.Timestamp):
        return int(dt.strftime("%Y%m%d"))
    else:
        return dt


def nanargsort(mat):
    new_mat = np.full_like(mat, np.nan)
    for i in np.arange(new_mat.shape[0]):
        arr_i = mat[i, :]
        mask = np.isnan(arr_i)
        new_mat[i, ~mask] = np.argsort(np.argsort(-arr_i[~mask])) < 2500  # 求最大
    return new_mat


def dict_configure(df, end_date):
    groups = df.groupby(df.index)
    config = {}
    for code, df in tqdm(groups):
        config[code] = stinfo_by_code(df, code, end_date)
    return config


def stinfo_by_code(df, code, end_date):
    df = df.sort_values(df.columns[0])
    array = df.loc[code].values.flatten()
    if np.isnan(array[-1]):
        array[-1] = end_date
    array = np.minimum(array, end_date)  # ipo 可能有未来的某一天上市信息
    mask = np.isnan(array)
    array = array[(~mask) & (~np.roll(mask, 1))]
    return array


@nb.jit(nopython=True, cache=True)
def match_amt(value, idx, ref_stt_idx, ref_end_idx):
    value = np.append([np.nan], value)
    fidx = np.append([ref_stt_idx], idx)
    bidx = np.roll(fidx, -1)
    bidx[-1] = ref_end_idx + 1
    amt = bidx - fidx
    return value, amt


def read_json(path, *args, **kwargs):
    with open(path, "r") as f:
        opt = json.load(f, *args, **kwargs)
    return opt


def save_json(obj, path, *args, **kwargs):
    with open(path, "w") as f:
        json.dump(obj, f, *args, **kwargs)


def read_datapath():
    user_config_path = str(Path(__file__).parent / "user_config.json")
    path = read_json(user_config_path)["data_path"]
    return path


def save_datapath(path):
    config_file = Path(__file__).parent / "user_config.json"
    if not config_file.exists():
        save_json({"data_path": path}, str(config_file))
    else:
        user_config = read_json(str(config_file))
        user_config["data_path"] = path
        save_json({"data_path": path}, str(config_file))


def read_version_config():
    fname = Path(read_datapath()) / "verison_info.json"
    verison_info =read_json(str(fname))
    return verison_info


def version_configuration():
    default_start_date = 20070101
    default_end_date = int(datetime.now().strftime('%Y%m%d'))
    cal_config = {
        "default_start_date": default_start_date,
        "default_end_date": default_end_date,
        "cal_config": {
            "Tday": {
                "si": 20070104,
                "ei": default_end_date,
                "col_name": "trade_dt"
            },
            "Aday": {
                "si": 20070101,
                "ei": default_end_date,
                "col_name": "ann_date"
            },
            "report_period": {
                "si": 20001231,
                "ei": default_end_date,
                "col_name": "report_period"
            }
        }
    }
    fname = Path(read_datapath()) / "verison_info.json"
    save_json(cal_config, str(fname))


def update_data(data_path=None, src_path="T:\\data\\new_api_data"):
    if data_path is None:
        data_path = Path(read_datapath())
    if data_path.exists():
        shutil.rmtree(str(data_path))
    tgt_path = str(data_path)
    shutil.copytree(src_path, tgt_path)


