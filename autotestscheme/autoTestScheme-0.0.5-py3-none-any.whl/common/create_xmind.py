#!/usr/bin/env python
# -*- coding:utf-8 -*-
import os
import re

import xmind
from . import config, constant

allure_report_dir = r'C:\Users\xiongrun\Downloads\allure-report\allure-report'
json_obj = config.Json(os.path.join(allure_report_dir, 'data', 'behaviors.json'))
if not os.path.exists(constant.XMIND_DIR):
    os.makedirs(constant.XMIND_DIR)
xmind_workbook_path = os.path.join(constant.XMIND_DIR, 'example.xmind')
case_title = '支付系统测试用例'
xmind_save_path = os.path.join(constant.XMIND_DIR, '{}.xmind'.format(case_title))

# 加载已有xmind文件，如果不存在，则新建
workbook = xmind.load(xmind_workbook_path)
first_sheet = workbook.getPrimarySheet()  # 获取第一个画布
first_sheet.setTitle(case_title)  # 设置画布名称
root_topic1 = first_sheet.getRootTopic()  # 获取画布中心主题，默认创建画布时会新建一个空白中心主题
root_topic1.setTitle(case_title)  # 设置主题名称

for i in json_obj.get_key('children'):
    sub_topic1 = root_topic1.addSubTopic()  # 创建子主题，并设置名称
    sub_topic1.setTitle(i.get('name'))
    for j in i.get('children'):
        sub_topic2 = sub_topic1.addSubTopic()
        sub_topic2.setTitle(j.get('name'))
        for v in j.get('children'):
            sub_topic3 = sub_topic2.addSubTopic()
            sub_topic3.setTitle(v.get('name'))
            if v.get('children') is not None:
                for k in v.get('children'):
                    try:
                        case_name = re.findall(r'\[(.*?)\]', k.get('name'))[0]
                    except Exception:
                        case_name = k.get('name')
                    sub_topic4 = sub_topic3.addSubTopic()
                    sub_topic4.setTitle(case_name)

xmind.save(workbook=workbook, path=xmind_save_path)  # 不改动原始文件，另存为其它xmind文件，等同 xmind.save(workbook, 'd:\\example\\exam.xmind')
