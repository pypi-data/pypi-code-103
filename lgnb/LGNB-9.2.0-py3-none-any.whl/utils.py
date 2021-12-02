#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   utils.py    
@Contact :   wangcc@csc.com.cn
@License :   (C)Copyright 2017-2018, CSC

@Modify Time      @Author    @Version    @Desciption
------------      -------    --------    -----------
2021/10/14 18:50   wangcc     1.0         None
'''


import numpy as np
import pandas as pd
from tqdm import tqdm
from .reader_utils import Cal
from .config import default_start_date, default_end_date, susday_config, suspension_config
from .tools import nanargsort, bisect_left, bisect_right, match_amt, dict_configure
calendar = Cal._get_calendar("Tday")


def create_ndns_table(index, cols, fill_value=False):
    table = pd.DataFrame(fill_value, index=index, columns=cols)
    return table


def to_ndns_reports(df, value_label, start_date, end_date, key1='report_period', key2='ann_date'):
    df['si'] = df[key2].apply(lambda x: bisect_left(calendar, x))
    dfs = {}
    ref_stt_idx = bisect_left(calendar, int(start_date))
    ref_end_idx = bisect_right(calendar, int(end_date)) - 1
    index = Cal.calendar(start_date, end_date)
    for inst, df_i in tqdm(df.groupby(df['code'])):
        df_i = df_i.sort_values([key2, key1]).drop_duplicates(key2, keep='last')
        value, amt = match_amt(df_i[value_label].values, df_i.si.values, ref_stt_idx, ref_end_idx)
        dfs[inst] = np.repeat(value, amt)
    return pd.DataFrame(dfs, index=index)


def to_ndns_io_date(df, time_keys, timeindex, stcoklist, end_date=default_end_date):
    """ st:"entry_date","remove_date"
        ipo:"listdate","delistdate"
        suspend"""
    tdict = dict_configure(df[time_keys], end_date)
    table_dict = {}
    for inst in tqdm(tdict.keys()):
        tlist = tdict.get(inst)
        if tlist is not None:
            sei = tlist.reshape((-1, 2))
            index = np.concatenate([Cal.calendar(si, ei) for si, ei in sei])
            table_dict[inst] = pd.Series(1, index=np.unique(index))
    return pd.concat(table_dict, axis=1).reindex(index=timeindex, columns=stcoklist)


def to_ndns_indu(indu, time_keys, timeindex, stcoklist, level):
    "entry_date	remove_date"
    indu = indu.reset_index().set_index('stockcode')[time_keys + [level]]
    ori_table = create_ndns_table(timeindex, stcoklist, np.nan)
    indu['remove_date'].fillna(int(default_end_date), inplace=True)
    transform_dict = dict(zip(indu.L1.unique(), range(indu.L1.unique().shape[0])))
    indu.L1 = indu.L1.map(transform_dict)
    for inst, si, ei, value in tqdm(indu.to_records()):
        ori_table.loc[si:ei, (inst,)] = value
        # print(inst)
    return ori_table.reindex(columns=stcoklist), transform_dict


def process_sus(sus):
    sus['is_sus'] = sus.suspend_type.map(suspension_config)
    sus = sus.loc[sus.is_sus]
    sus['replace'] = sus.suspend_type.map(susday_config) & np.isnan(sus.resump_date)
    sus.loc[sus['replace'], 'resump_date'] = sus.loc[sus['replace'], 'suspend_date']
    return sus







