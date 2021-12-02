#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   reader_utils.py    
@Contact :   wangcc@csc.com.cn
@License :   (C)Copyright 2017-2018, CSC

@Modify Time      @Author    @Version    @Desciption
------------      -------    --------    -----------
2021/10/15 10:44   wangcc     1.0         None
'''

import json
import glob
from joblib import Parallel, delayed
import copy
import os
import re
import pandas as pd
import numpy as np
import time
import h5py
import logging
from pyarrow.dataset import field as ffield
from pyarrow import dataset as ds
from typing import Union, Iterable
from pathlib import Path
from .tools import bisect_left, bisect_right, to_intdate, read_version_config
from .config import data_path, cal_config

markets = ["zz500", "hs300", "zz800", "zz1000", "all"]
logger = logging.getLogger("logger")
stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.WARNING)
formatter = logging.Formatter("%(asctime)s %(name)s %(levelname)s %(message)s")
logger.addHandler(stream_handler)


class BaseProvider:
    """ data prov"""

    def calendar(self, start_time=None, end_time=None, freq="Tday"):
        """
        :param start_time
        :param end_time
        :param freq: includdes Aday for natural day; Tday for trading day; report_period for financial statement
        :return:
        """
        return Cal.calendar(start_time, end_time, freq)

    def list_instruments(self, instruments, start_time=None, end_time=None, freq="Tday", as_list=False):
        """
        :param instruments: instruments list or market (ei. "zz500", "hs300", "zz800", "zz1000", "all"
        :param start_time:
        :param end_time:
        :param freq: includdes Aday for natural day; Tday for trading day; report_period for financial statement
        :param as_list: if as_list, return list of instruments, else return dict with values of inday-outday span
        :return:
        """
        return Inst.list_instruments(instruments, start_time, end_time, freq, as_list)

    def list_features(self, freq="*"):
        """
        :param freq: includdes Aday for natural day; Tday for trading day; report_period for financial statement
        :return: list of features
        """
        return list_features(freq)

    def feature_info(self, field, freq):
        """
        return the config of the field
        :param field: features str
        :param freq: includdes Aday for natural day; Tday for trading day; report_period for financial statement
        :return:
        """
        return FeatureD.feature_info(field, freq)

    def features(self, fields, start_time=None, end_time=None, freq="Tday", return_mat=False, instruments="all"):
        """
        :param instruments: instruments list or market (ei. "zz500", "hs300", "zz800", "zz1000", "all"
        :param fields: features str or list
        :param start_time:
        :param end_time:
        :param freq: includdes Aday for natural day; Tday for trading day; report_period for financial statement
        :param return_mat: if return_mat, return nd-ns numpy array
        :return:
        """
        if isinstance(fields, str):
            fields = [fields, ]
        if freq == "report_period":
            fields += ["ann_date", ]
        fields = list(fields)  # In case of tuple.
        return FeatureD.features(instruments, fields, start_time, end_time, freq, return_mat)

    def features_mmat(self, fields, start_time=None, end_time=None, freq="Tday", instruments="all"):
        """
        :param instruments: instruments list or market (ei. "zz500", "hs300", "zz800", "zz1000", "all"
        :param fields: features str or list
        :param start_time:
        :param end_time:
        :param freq: includdes Aday for natural day; Tday for trading day; report_period for financial statement
        :return: DataFrames that may have different shapes
        """
        if isinstance(fields, str):
            fields = [fields, ]
        if freq == "report_period":
            fields += ["ann_date", ]
        fields = list(fields)  # In case of tuple.
        return FeatureD.features_mmat(instruments, fields, start_time, end_time, freq)

    def features_tday(self, fields, start_time=None, end_time=None, return_mat=False, instruments="all"):
        """
        :param instruments: instruments list or market (ei. "zz500", "hs300", "zz800", "zz1000", "all"
        :param fields:  features str or list
        :param start_time:
        :param end_time:
        :param return_mat:
        :return:
        """
        return self.features(fields, start_time, end_time, "Tday", return_mat, instruments)

    def features_aday(self, fields, start_time=None, end_time=None, return_mat=False, instruments="all"):
        """
        :param instruments: instruments list or market (ei. "zz500", "hs300", "zz800", "zz1000", "all"
        :param fields:  features str or list
        :param start_time:
        :param end_time:
        :param return_mat:
        :return:
        """
        return self.features(fields, start_time, end_time, "Aday", return_mat, instruments)

    def features_rpday(self, fields, start_time=None, end_time=None, return_mat=False, instruments="all"):
        """
        :param instruments: instruments list or market (ei. "zz500", "hs300", "zz800", "zz1000", "all"
        :param fields:  features str or list
        :param start_time:
        :param end_time:
        :param return_mat:
        :return:
        """
        return self.features(fields, start_time, end_time, "report_period", return_mat, instruments)

    def list_datasets(self):
        """
        :return:  list of dataset name
        """
        return list_datasets()

    def dataset_info(self, dataset):
        """
        :param dataset: dataset name
        :return: the columns with dtype info of the dataset
        """
        return DatasetD.dataset_info(dataset)

    def datasets(self, dataset, instruments="all", fields=None, start_time=None, end_time=None):
        """
        :param instruments: instruments list or market (ei. "zz500", "hs300", "zz800", "zz1000", "all"
        :param fields:  features str or list
        :param start_time:
        :param end_time:
        :param dataset: dataset name
        :return:
        """
        if isinstance(fields, str):
            fields = [fields, ]
        if fields is None:
            _, _, others, _, _ = DatasetD.dataset_info(dataset)
            fields = list(others.keys())
        fields = list(fields)
        return DatasetD.datasets(instruments, fields, start_time, end_time, dataset)

    def datasets_fl(self, dataset, fields=None, filt=None, **kwargs):
        """
        :param filt: conditions to filt the dataset
        :param fields:
        :param dataset: dataset name
        :param kwargs: the args to evaluate the filter statement
        :return:
        """
        if isinstance(fields, str):
            fields = [fields, ]
        if fields is None:
            _, _, others, _, _ = DatasetD.dataset_info(dataset)
            fields = list(others.keys())
        fields = list(fields)
        return DatasetD.datasets_fl(filt, fields, dataset, **kwargs)

    def version_info(self):
        return read_version_config()


class CalendarProvider:
    """Calendar provider base class: Provide calendar data."""

    def __init__(self):
        self.cal_cache = {}

    @property
    def _uri_cal(self):
        return os.path.join(data_path, "calendars", "{}.txt")

    def cache_cal(self, freq: str = "Tday"):
        _calendar = np.array(self.load_calendar(freq))
        _calendar_index = {x: i for i, x in enumerate(_calendar)}  # for fast search
        self.cal_cache[freq] = (_calendar, _calendar_index)

    def load_calendar(self, freq: str = "Tday"):
        """Load original int calendar from file."""

        fname = self._uri_cal.format(freq)
        if not os.path.exists(fname):
            raise ValueError("calendar not exists for freq " + freq)
        with open(fname) as f:
            return [int(x.strip()) for x in f]

    def calendar(self, start_time=None, end_time=None, freq="Tday"):
        _calendar, _ = self._get_calendar(freq)
        if start_time == "None":
            start_time = None
        if end_time == "None":
            end_time = None
        # strip
        if start_time:
            start_time = to_intdate(start_time)
            if start_time > _calendar[-1]:
                return np.array([])
        else:
            start_time = cal_config[freq]["si"]
        if end_time:
            end_time = to_intdate(end_time)
            if end_time < _calendar[0]:
                return np.array([])
        else:
            end_time = cal_config[freq]["ei"]
        si, ei = self.locate_index(start_time, end_time, freq)
        return _calendar[si: ei + 1]

    def locate_index(self, start_time, end_time, freq='Tday'):
        """Locate the start time index and end time index in a calendar under certain frequency."""
        try:
            start_time = to_intdate(start_time)
        except:
            pass
        end_time = to_intdate(end_time)
        calendar, calendar_index = self._get_calendar(freq=freq)
        if start_time not in calendar_index:
            try:
                start_time = calendar[bisect_left(calendar, start_time)]
            except IndexError:
                raise IndexError(
                    f"`start_time` doesnt exist in {freq} calendar`"
                )
        start_index = calendar_index[start_time]
        if end_time not in calendar_index:
            end_time = calendar[bisect_right(calendar, end_time) - 1]
        end_index = calendar_index[end_time]
        return start_index, end_index

    def _get_calendar(self, freq: str = "Tday"):
        """Load calendar using memcache."""
        if freq in self.cal_cache:
            return self.cal_cache.get(freq)
        else:
            self.cache_cal(freq)
            return self.cal_cache.get(freq)

    def cal_shifts(self, dt, shifts, freq: str = "Tday"):
        calendar, calendar_index = self._get_calendar(freq=freq)
        if isinstance(dt, Iterable):
            predt = np.array([self.cal_shifts(dt_i, shifts, freq) for dt_i in dt])
            return predt
        else:
            if shifts > 0:
                index = self.cal_loc(dt, "b", freq)
                if calendar_index.get(dt) is None:
                    shifts -= 1
            else:
                index = self.cal_loc(dt, "f", freq)
                if calendar_index.get(dt) is None:
                    shifts = min(0, shifts + 1)
        return calendar[index + shifts]

    def cal_delta(self, sdt, edt, freq: str = "Tday"):
        """return diff between dates"""
        si = self.cal_loc(sdt, "f", freq)
        ei = self.cal_loc(edt, "f", freq)
        return ei - si

    def near_dts(self, dt, mode: str = "f", freq: str="Tday"):
        _calendar, _calendar_index = self._get_calendar(freq=freq)
        locations = self.cal_loc(dt, mode, freq)
        return _calendar[locations]

    def cal_loc(self, dt: Iterable, mode: str = "f", freq: str = "Tday"):
        """
        :param dt: int or iterable
        :param mode: f for forward or b for backward if dt not in calendar index
        :param freq:
        :return: int or nparray
        """
        calendar, calendar_index = self._get_calendar(freq=freq)
        if isinstance(dt, Iterable):
            index = np.array([self.cal_loc(dt_i, mode, freq) for dt_i in dt])
        elif isinstance(dt, int):
            if dt not in calendar_index:
                try:
                    if mode == "f":
                        dt = calendar[bisect_right(calendar, dt) - 1]
                    else:
                        dt = calendar[bisect_left(calendar, dt)]
                except IndexError:
                    raise IndexError(
                        f"`start_time` doesnt exist in {freq} calendar`"
                    )
            index = calendar_index[dt]
        else:
            raise TypeError("dt is not int or iterable")
        return index


class InstrumentProvider:
    """Instrument provider base class:Provide instrument data."""

    @property
    def _uri_inst(self):
        """Instrument file uri."""
        return os.path.join(data_path, "instruments", "{}.txt")

    def _load_instruments(self, market):
        fname = self._uri_inst.format(market)
        if not os.path.exists(fname):
            raise ValueError("instruments not exists for market " + market)

        _instruments = dict()
        df = pd.read_csv(
            fname,
            sep="\t",
            usecols=[0, 1, 2],
            names=["inst", "start_datetime", "end_datetime"],
            dtype={"inst": str},
            # parse_dates=["start_datetime", "end_datetime"],
        )
        for row in df.itertuples(index=False):
            _instruments.setdefault(row[0], []).append((row[1], row[2]))
        return _instruments

    def list_instruments(self, instruments, start_time=None, end_time=None, freq="Tday", as_list=False):
        if isinstance(instruments, str):
            market = instruments
        else:
            market = instruments["market"]

        _instruments = self._load_instruments(market)
        # strip
        # use calendar boundary
        cal = Cal.calendar(freq=freq)
        start_time = to_intdate(start_time or cal[0])
        end_time = to_intdate(end_time or cal[-1])
        _instruments_filtered = {
            inst: list(
                filter(
                    lambda x: x[0] <= x[1],
                    [(max(start_time, x[0]), min(end_time, x[1])) for x in spans],
                )
            )
            for inst, spans in _instruments.items()
        }
        _instruments_filtered = {key: value for key, value in _instruments_filtered.items() if value}
        # as list
        if as_list:
            return list(_instruments_filtered)
        return _instruments_filtered


class BaseDataProvider:

    @staticmethod
    def get_instruments_d(instruments, start_time, end_time, freq):
        """
        Parse different types of input instruments to output instruments_d
        Wrong format of input instruments will lead to exception.

        """
        if isinstance(instruments, dict):
            if "market" in instruments:
                # dict of stockpool config
                instruments_d = Inst.list_instruments(instruments=instruments, start_time=start_time,
                                                      end_time=end_time, freq=freq, as_list=False)
            else:
                # dict of instruments and timestamp
                instruments_d = instruments
        elif isinstance(instruments, str):
            if instruments in markets:
                instruments_d = Inst.list_instruments(instruments=instruments, start_time=start_time,
                                                      end_time=end_time, freq=freq, as_list=False)
            else:
                instruments_d = [instruments, ]

        elif isinstance(instruments, (list, tuple, pd.Index, np.ndarray)):
            # list or tuple of a group of instruments
            instruments_d = list(instruments)
        else:
            raise ValueError("Unsupported input type for param `instrument`")
        return instruments_d

    @staticmethod
    def get_column_names(fields):
        """
        Get column names from input fields

        """
        if len(fields) == 0:
            raise ValueError("fields cannot be empty")
        fields = fields.copy()
        column_names = [str(f) for f in fields]
        return column_names

    @staticmethod
    def remove_repeat_field(fields):
        """remove repeat field

        :param fields: list; features fields
        :return: list
        """
        fields = copy.deepcopy(fields)
        _fields = set(fields)
        return sorted(_fields, key=fields.index)

    @staticmethod
    def normalize_cache_fields(fields: [list, tuple]):
        """normalize cache fields

        :param fields: features fields
        :return: list
        """
        fields = [i for i in fields if i is not None]
        return BaseDataProvider.remove_repeat_field(fields)


class FeatureProvider(BaseDataProvider):
    """Dataset provider class: Provide Dataset data."""

    @property
    def _uri_data(self):
        return os.path.join(data_path, "features", "{}", "{}.h5")

    @property
    def _uri_cfg(self):
        """Static feature file uri."""
        return os.path.join(data_path, "features", "{}", "{}_config.json")

    def features(self, instruments, fields, start_time=None, end_time=None, freq="Tday", return_mat=False):
        instruments_d = self.get_instruments_d(instruments, start_time, end_time, freq)
        column_names = self.get_column_names(fields)
        cal = Cal.calendar(start_time, end_time, freq)
        if len(cal) == 0:
            return pd.DataFrame(columns=column_names)
        start_time = cal[0]
        end_time = cal[-1]
        data = self.feature_processor(self._uri_data, instruments_d, column_names, start_time, end_time, freq,
                                      return_mat)
        return data

    def features_mmat(self, instruments, fields, start_time=None, end_time=None, freq="Tday"):
        instruments_d = self.get_instruments_d(instruments, start_time, end_time, freq)
        column_names = self.get_column_names(fields)
        cal = Cal.calendar(start_time, end_time, freq)
        if len(cal) == 0:
            return pd.DataFrame(columns=column_names)
        start_time = cal[0]
        end_time = cal[-1]
        data = self.feature_processor_mmat(self._uri_data, instruments_d, column_names, start_time, end_time, freq)
        return data

    def feature_info(self, field, freq):
        config_path = self._uri_cfg.format(freq, field)
        return FeatureD.read_config(config_path)

    @staticmethod
    def feature_processor(fpath, instruments_d, column_names, start_time, end_time, freq, return_mat=False):
        """
        Load and process the data, return the data set.
        - default using multi-kernel method.

        """
        # One process for one task, so that the memory will be freed quicker.
        if isinstance(instruments_d, dict):
            instruments_d = list(instruments_d.keys())
        instruments_d = np.array(instruments_d)
        dtname = cal_config[freq]["col_name"]
        normalize_column_names = FeatureD.normalize_cache_fields(column_names)
        stk_univ, time_idx, inst_mask, time_mask, mmp_shape = read_mask(fpath.format(freq, dtname), instruments_d,
                                                                        start_time, end_time, freq)
        if not time_mask.any():
            return pd.DataFrame(columns=column_names)

        workers = min(kernels, len(instruments_d))
        start = time.perf_counter()

        field_l = []
        tasks_l = []
        for field in normalize_column_names:
            field_l.append(field)
            tasks_l.append(
                delayed(read_mmap)(
                    fpath.format(freq, field), "data", inst_mask, time_mask, mmp_shape
                )
            )

        data = dict(
            zip(
                field_l,
                Parallel(n_jobs=workers, backend="threading")(tasks_l),
            )
        )
        if return_mat:
            data = {
                k: v.T for k, v in data.items() if v is not None
            }
            data["stockcode"] = stk_univ[inst_mask]
            data[dtname] = time_idx[time_mask]
        else:
            data = {
                k: v.flatten() for k, v in data.items() if v is not None
            }
            multiindex = pd.MultiIndex.from_product([stk_univ[inst_mask], time_idx[time_mask]],
                                                    names=["stockcode", cal_config[freq]["col_name"]])
            data = pd.DataFrame(data, index=multiindex).reset_index()
        print(time.perf_counter() - start)
        return data

    @staticmethod
    def feature_processor_mmat(fpath, instruments_d, column_names, start_time, end_time, freq):
        """
        Load and process the data, return the data set.
        - default using multi-kernel method.

        """
        # One process for one task, so that the memory will be freed quicker.
        if isinstance(instruments_d, dict):
            instruments_d = list(instruments_d.keys())
        instruments_d = np.array(instruments_d)
        normalize_column_names = FeatureD.normalize_cache_fields(column_names)

        workers = min(kernels, len(instruments_d))
        start = time.perf_counter()

        field_l = []
        tasks_l = []
        for field in normalize_column_names:
            field_l.append(field)
            tasks_l.append(
                delayed(read_mmat)(
                    fpath.format(freq, field), instruments_d, start_time, end_time, freq
                )
            )

        data = dict(
            zip(
                field_l,
                Parallel(n_jobs=workers, backend="threading")(tasks_l),
            )
        )
        data = {
            k: v for k, v in data.items() if v is not None
        }
        print(time.perf_counter() - start)
        return data

    @staticmethod
    def read_config(config_path):
        if not os.path.exists(config_path):
            print("No config fund")
            return {}
        with open(config_path, "r") as f:
            json_cfg = json.load(f)
        return json_cfg


class DatasetProvider(BaseDataProvider):
    """Dataset provider class: Provide Dataset data."""

    @property
    def _uri_data(self):
        return os.path.join(data_path, "datasets", "{}")

    def datasets(self, instruments, fields, start_time=None, end_time=None, dataset=None):
        instruments_d = self.get_instruments_d(instruments, start_time, end_time, freq="Aday")
        column_names = self.get_column_names(fields)
        cal = Cal.calendar(start_time, end_time, "Aday")
        if len(cal) == 0:
            return pd.DataFrame(columns=column_names)
        start_time = cal[0]
        end_time = cal[-1]
        fpath = self._uri_data.format(dataset)
        data = self.dataset_processor(fpath, instruments_d, column_names, start_time, end_time)
        return data

    def datasets_fl(self, filt, fields, dataset, **kwargs):
        column_names = self.get_column_names(fields)
        fpath = self._uri_data.format(dataset)
        data = self.dataset_processor_fl(fpath, filt, column_names, **kwargs)
        return data

    def dataset_info(self, dataset):
        config_path = os.path.join(self._uri_data.format(dataset),  "config.json")
        return DatasetD.read_config(config_path)

    @staticmethod
    def dataset_processor(fpath, instruments_d, column_names, start_time=None, end_time=None):
        """
        :param fpath:
        :param instruments_d:
        :param column_names:
        :param start_time:
        :param end_time:
        :return:
        """
        # One process for one task, so that the memory will be freed quicker.
        normalize_column_names = DatasetD.normalize_cache_fields(column_names)
        config_path = os.path.join(fpath, "config.json")
        code_flt, time_flt, _, is_annrepo, format_ = DatasetD.read_config(config_path)
        primary_keys = [code_flt, time_flt]  # 插入primary key
        if is_annrepo:
            primary_keys += ["report_period"]
        normalize_column_names = DatasetD.normalize_cache_fields(primary_keys + normalize_column_names)
        code_flt = ffield(code_flt) if code_flt is not None else None
        time_flt = ffield(time_flt) if time_flt is not None else None
        if format_ == "feather":
            flist = glob.glob(os.path.join(fpath, "*[!.json]"))
        else:
            flist = glob.glob(os.path.join(fpath, "**", "*"))
        dset = ds.dataset(flist, format=format_)  # 还差不规则特征

        if code_flt is None:
            if time_flt is None:
                return dset.to_table(columns=normalize_column_names).to_pandas()
            else:
                condition = (time_flt >= start_time) & (time_flt <= end_time)
        else:
            if time_flt is None:
                condition = code_flt.isin(instruments_d)
            else:
                condition = (time_flt >= start_time) & (time_flt <= end_time) & (code_flt.isin(instruments_d))
        start = time.perf_counter()
        data = dset.to_table(columns=normalize_column_names, filter=condition).to_pandas()
        print(time.perf_counter() - start)
        return data

    @staticmethod
    def dataset_processor_fl(fpath, filt, column_names, **kwargs):
        """
        :param fpath:
        :param filt: str or instance of pyarrow.dataset.field
        :param column_names:
        :param kwargs:
        :return:
        """
        # One process for one task, so that the memory will be freed quicker.
        config_path = os.path.join(fpath, "config.json")
        code_flt, time_flt, _, is_annrepo, format_ = DatasetD.read_config(config_path)
        primary_keys = [code_flt, time_flt]  # 插入primary key
        if is_annrepo:
            primary_keys += ["report_period"]
        column_names = primary_keys + column_names

        normalize_column_names = DatasetD.normalize_cache_fields(column_names)
        if format_ == "feather":
            flist = glob.glob(os.path.join(fpath, "*[!.json]"))
        else:
            flist = glob.glob(os.path.join(fpath, "**", "*"))
        dset = ds.dataset(flist, format=format_)
        # 还差不规则特征
        start = time.perf_counter()
        if filt is None:
            data = dset.to_table(columns=normalize_column_names).to_pandas()
        else:
            for k in kwargs.keys():
                exec(f"{k}=kwargs['{k}']")
            if isinstance(filt, str):
                filt = eval(parse_field(filt))
            data = dset.to_table(columns=normalize_column_names, filter=filt).to_pandas()
        print(time.perf_counter() - start)
        return data

    @staticmethod
    def read_config(config_path):
        with open(config_path, "r") as f:
            json_cfg = json.load(f)
            code_flt = json_cfg["code_flt"]
            time_flt = json_cfg["time_flt"]
            others = json_cfg["others"]
            is_annrepo = json_cfg["is_annrepo"]
            format_ = json_cfg.get("format", "feather")
        return code_flt, time_flt, others, is_annrepo, format_


def list_features(freq="*"):
    features = (Path(data_path) / "features").glob(f"**/{freq}/*.h5")
    features = [i.name.replace(".h5", "") for i in features]
    return features


def list_datasets():
    datasets = (Path(data_path) / "datasets").glob("*")
    datasets = [i.name for i in datasets if i.is_dir()]
    return datasets


def read_mmat(pth, ori_instruments, start_time, end_time, freq):
    """numpy 数据结构提取, mmap加速"""
    name = Path(pth).name.split(".")[0]
    if not os.path.exists(pth):
        logger.warning(f"WARN feature {name} not found")
        return pd.DataFrame()
    stk_univ, time_idx, inst_mask, time_mask, shape = read_mask(pth, ori_instruments, start_time, end_time, freq)
    arr = read_mmap(pth, "data", inst_mask, time_mask, shape)
    if arr is None:
        return pd.DataFrame()
    opt = pd.DataFrame(arr.T, index=time_idx[time_mask], columns=stk_univ[inst_mask])
    opt.index.names = [cal_config[freq]["col_name"]]
    opt.columns.names = ["stockcode"]
    return opt


def read_mmap(pth, key, inst_mask, time_mask, mmp_shape):
    """numpy 数据结构提取, mmap加速"""
    name = Path(pth).name.split(".")[1]
    if not os.path.exists(pth):
        logger.warning(f"WARN feature {name} not found")
        return None
    with h5py.File(pth, 'r') as f:
        ds = f[key]
        offset = ds.id.get_offset()
        assert ds.chunks is None
        assert ds.compression is None
        assert offset > 0
        dtype = ds.dtype
        shape = ds.shape
    arr = np.memmap(pth, mode='r', shape=shape, offset=offset, dtype=dtype)
    try:
        arr = arr.reshape(mmp_shape)
        return arr[:, time_mask][inst_mask, :]
    except:
        name = Path(pth).name.split(".")[1]
        logger.warning(f"mask mismatch, feature {name} has different shape, please load it seperately")
        return None


def constru_index(pth, freq):
    start_time, end_time = read_index(pth)
    stk_univ = sorted(list(Inst.list_instruments("all", start_time, end_time, freq).keys()))
    time_idx = Cal.calendar(start_time, end_time, freq=freq)
    return np.array(stk_univ), time_idx, (len(stk_univ), len(time_idx))


def read_index(pth):
    with h5py.File(pth, 'r') as f:
        start_time = f["data"].attrs["start_time"]
        end_time = f["data"].attrs["end_time"]
    return start_time, end_time


def read_mask(path, ori_instruments, start_time, end_time, freq):
    stk_univ, time_idx, shape = constru_index(path, freq)
    inst_mask = np.in1d(stk_univ, ori_instruments)
    time_mask = (time_idx >= start_time) & (time_idx <= end_time)
    return stk_univ, time_idx, inst_mask, time_mask, shape


def parse_field(field):
    if not isinstance(field, str):
        field = str(field)
    return re.sub(r"\$(\w+)", r'ffield("\1")', field)


DatasetD = DatasetProvider()
FeatureD = FeatureProvider()
Cal = CalendarProvider()
Inst = InstrumentProvider()
D = BaseProvider()

kernels = 20
