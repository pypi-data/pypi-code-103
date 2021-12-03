# -*- coding: utf-8 -*-
'''
@File  : table.py
@Author: Jike Data Analysis Modeling Group
@Date  : 2021/12/4 12:13 上午
@Desc  : hive表
'''

WIFI_STABLE_LOCALTION_TABLE = 'db_tmp.tmp_wifi_stable_poi_data_d' # 稳定点位表
WIFI_CONNECTED__LOCATION_TABLE = 'db_tmp.tmp_wifi_appearance_poi_data_d' # 连接点位表
POI_ARRIVED_LOCATION_TABLE = 'db_dw.wd_scene_log_h' # poi到访点位表
POI_LEAVE_EVENT_TABLE = 'db_dw.wd_geek_event_h' # poi离店事件表
POI_TABLE = 'db_ods.s_geek_poi' # poi属性表
POI_CATEGOIRES_TABLE = 'db_ods.s_geek_categories' # poi分类表表