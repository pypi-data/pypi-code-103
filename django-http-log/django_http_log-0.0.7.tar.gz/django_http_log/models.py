#!/user/bin/env python3
# -*- coding: utf-8 -*-
"""
--------------------------------------
    Author:     JiChao_Song
    Date  :     2021/11/20 下午10:52
    Desc  :
--------------------------------------
"""
from mongoengine import fields, Document


class Log(Document):
    path = fields.StringField()  # 请求路径
    method = fields.StringField()  # 请求方案
    ip = fields.StringField()  # 请求Ip
    scheme = fields.StringField()  # 其他参数
    status = fields.IntField()  # http状态码
    request_body = fields.StringField()  # 请求体
    request_header = fields.DictField()  # 请求头
    response_body = fields.StringField()  # 响应体
    response_header = fields.DictField()  # 响应牛头
    startTime = fields.IntField()  # 开始时间
    endTime = fields.IntField()  # 结束时间
    operateType = fields.StringField()  # 操作类型
    operateContent = fields.StringField()  # 操作类型
    operatorId = fields.IntField()  # 操作人id
    operatorName = fields.StringField()  # 操作人姓名
    operateTime = fields.IntField()  # 操作时间

    meta = {
        'verbose_name': '请求日志',
        'ordering': ['-operateTime'],
        'indexes': [
            'path',
            'method',
            'operatorName'
        ]
    }
