#!/user/bin/env python3
# -*- coding: utf-8 -*-
"""
--------------------------------------
    Author:     JiChao_Song
    Date  :     2021/11/20 下午10:52
    Desc  :
--------------------------------------
"""
from django.apps import AppConfig

__all__ = ['LogConfig']


class LogConfig(AppConfig):

    name = 'django_http_log'
    label = 'django_http_log'
    default_auto_field = 'django.db.models.AutoField'
