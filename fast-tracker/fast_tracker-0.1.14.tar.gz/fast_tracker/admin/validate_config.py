# -*- coding: utf-8 -*-
from __future__ import print_function

from fast_tracker.admin import command


@command('validate-config', 'config_file [log_file]',
         """校验配置参数""")
def validate_config(args):
    pass
