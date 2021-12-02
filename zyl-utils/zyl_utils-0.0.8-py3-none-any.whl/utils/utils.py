# encoding: utf-8
'''
@author: zyl
@file: utils.py
@time: 2021/11/11 9:35
@desc:
'''

import pandas as pd


def use_cmd_argument():
    import argparse

    parser = argparse.ArgumentParser(description='set some parameters')

    parser.add_argument('--', type=str, help='传入的数字',default='a')
    parser.add_argument('--', type=str, help='传入的数字', default='a')
    parser.add_argument('--', type=str, help='传入的数字', default='a')
    parser.add_argument('--', type=str, help='传入的数字', default='a')
    parser.add_argument('--', type=str, help='传入的数字', default='a')
    parser.add_argument('--', type=str, help='传入的数字', default='a')
    parser.add_argument('--', type=str, help='传入的数字', default='a')
    parser.add_argument('--', type=str, help='传入的数字', default='a')
    parser.add_argument('--', type=str, help='传入的数字', default='a')
    parser.add_argument('--', type=str, help='传入的数字', default='a')
    parser.add_argument('--', type=str, help='传入的数字', default='a')
    parser.add_argument('--', type=str, help='传入的数字', default='a')
    parser.add_argument('--', type=str, help='传入的数字', default='a')
    parser.add_argument('--', type=str, help='传入的数字', default='a')
    parser.add_argument('--', type=str, help='传入的数字', default='a')
    parser.add_argument('--', type=str, help='传入的数字', default='a')
    parser.add_argument('--', type=str, help='传入的数字', default='a')


    args = parser.parse_args()

    # 获得integers参数
    print(args.integers)
    return args



    parser.add_argument('integers', metavar='N', type=int, nargs='+',
                        help='an integer for the accumulator')
    parser.add_argument('--sum', dest='accumulate', action='store_const',
                        const=sum, default=max,
                        help='sum the integers (default: find the max)')

    args = parser.parse_args()
    print(args.accumulate(args.integers))




class Utils:
    def __init__(self):
        pass

    @staticmethod
    def to_excel(dataframe, excel_path, sheet_name='default'):
        try:
            from openpyxl import load_workbook
            book = load_workbook(excel_path)
            writer = pd.ExcelWriter(excel_path, engine='openpyxl')
            writer.book = book
        except:
            writer = pd.ExcelWriter(excel_path, engine='openpyxl')

        dataframe.to_excel(writer, sheet_name=sheet_name, index=False)
        writer.save()
