#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   saver_utils.py    
@Contact :   wangcc@csc.com.cn
@License :   (C)Copyright 2017-2018, CSC

@Modify Time      @Author    @Version    @Desciption
------------      -------    --------    -----------
2021/10/15 10:24   wangcc     1.0         None
'''


import json
import h5py
import pandas as pd
import numpy as np
from pandas import DataFrame, Series
from .config import data_path
from .reader_utils import Cal, Inst
from .tools import read_version_config
import os


class FeatureUpdater:

    def __init__(self, stk_univ="all", start_time=None, end_time=None, freq="Tday", is_alpha=False):
        self.cal_config = read_version_config()["cal_config"]
        start_time = self.cal_config[freq]["si"] if start_time is None else start_time
        end_time = self.cal_config[freq]["ei"] if end_time is None else end_time
        _, calendar_index = Cal._get_calendar(freq=freq)
        self.stk_univ = sorted(list(Inst.list_instruments(stk_univ, start_time, end_time).keys()))
        self.time_idx = Cal.calendar(start_time, end_time, freq=freq)
        self.multiidx = pd.MultiIndex.from_product([self.stk_univ, self.time_idx])
        self.freq = freq
        self.start_time = start_time
        self.end_time = end_time
        self.is_alpha = is_alpha

    @property
    def _uri_data(self):
        """Static feature file uri."""
        return os.path.join(data_path, "features", "{}", "{}.h5")

    @property
    def _uri_cfg(self):
        """Static feature file uri."""
        return os.path.join(data_path, "features", "{}", "{}_config.json")

    def _get_uri(self, freq, field):
        main_path = os.path.join(data_path, "features", f"{freq}")
        if not os.path.exists(main_path):
            os.mkdir(main_path)
        return self._uri_data.format(self.freq, field)

    def save_series(self, field: str, values: Series, config: dict):
        flname = self._get_uri(self.freq, field)
        if values.values.dtype == np.object_:
            return
        with h5py.File(flname, "w") as h5:
            h5.create_dataset("data", data=values.values)
            h5["data"].attrs["start_time"] = self.start_time
            h5["data"].attrs["end_time"] = self.end_time
            if config:
                with open(self._uri_cfg.format(self.freq, field), "w") as f:
                    json.dump(config, f)

    def save_values(self, Mdf: DataFrame, dtname: str, partition_by: str, config: dict= None):
        Mdf = self._locate_partition(Mdf, dtname, partition_by)
        if config is None:
            config = {}
        value_dict = Mdf.to_dict("series")
        if self.is_alpha:
            value_dict.pop(self.cal_config[self.freq]["col_name"])
        for field, values in value_dict.items():
            config_i = config.get(field, None)
            self.save_series(field, values, config_i)

    def _locate_partition(self, Mdf: DataFrame, dtname: str, partition_by: str):
        """
        partition Mdf according to instruments
        :param Mdf:
        :param dtname:
        :param partition_by:
        :return:
        """
        order_by = [partition_by, dtname]
        self.multiidx.names = order_by
        Mdf = Mdf.set_index(order_by).reindex(self.multiidx).reset_index()  # 要改
        return Mdf.set_index(partition_by)


class FeatureSaver(FeatureUpdater):

    def __init__(self, freq):
        super().__init__(freq=freq)

    def save_alpha(self, alpha, alpha_name, config=None):
        alpha = alpha.rename(columns={"value": alpha_name})
        self.save_values(alpha, self.cal_config[self.freq]["col_name"], "stockcode", config)


print("res")