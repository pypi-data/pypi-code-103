#!/usr/local/bin/python
# coding:utf-8

from paradoxapi.common.gateway import *

if __name__ == '__main__':
    codes = ['000002', '600000', '600519', '600588']
    # start = '2021-01-01'
    end = '2021-11-01'
    fields = ['', '', '', '']
    df = get_balance_sheet_fore_annual(codes, end=end)
    print(df)


