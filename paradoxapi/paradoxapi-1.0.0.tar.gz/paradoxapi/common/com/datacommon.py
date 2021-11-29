#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author:HDD

def get_db(env='pro', data_type='Pld_data', db='hermes'):
    # 获取数据库信息
    mysql_dicc = all_db_filed(db)
    return mysql_dicc[data_type + '_' + env]

def all_db_filed(db='hermes'):
    '''
    MySQL信息：
    '''

    mysql_dic = {
        'Pld_data_pro': {'host': '168_157_146_150_158_143_167_170_147_163_102_149_',
                         'user': '229_223_201_209_',
                         'pwd': '224_205_214_192_209_208_235_165_155_170_',
                         'port': 3306,
                         'db': db}}
    return mysql_dic
