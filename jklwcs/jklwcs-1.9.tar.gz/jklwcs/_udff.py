# -*- coding: utf-8 -*-
'''
@File  : _udff.py
@Author: Jike Data Analysis Modeling Group
@Date  : 2021/12/4 12:13 上午
@Desc  : 自定义udf函数
'''

from pyspark.sql.functions import udf

@udf
def _get_category(c_id_list,c_id_categories_map):
    # c_id查询分类
    c_name_list = []
    if not c_id_list:
        return '_'.join(['','',''])

    c_id_list = eval(c_id_list)

    if len(c_id_list) == 1:
        c_id_list.extend(['M','N'])

    if len(c_id_list) == 2:
        c_id_list.extend(['M'])

    for c_id in c_id_list:
        c_name_list.append(c_id_categories_map.get(c_id,''))

    return '_'.join(c_name_list)