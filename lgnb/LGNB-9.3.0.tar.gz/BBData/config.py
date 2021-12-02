#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   config.py    
@Contact :   wangcc@csc.com.cn
@License :   (C)Copyright 2017-2018, CSC

@Modify Time      @Author    @Version    @Desciption
------------      -------    --------    -----------
2021/10/14 17:03   wangcc     1.0         None
'''


from pathlib import Path
import platform
from .tools import read_datapath, read_version_config
version_info = read_version_config()
default_start_date = version_info["default_start_date"]
default_end_date = version_info["default_end_date"]
cal_config = version_info["cal_config"]

susday_config = {
    444001000: True,  # 上午停牌
    444002000: True,  # 下午停牌
    444003000: False,  # 今起停牌
    444004000: True,  # 盘中停牌
    444005000: True,  # 停牌半天
    444007000: True,  # 停牌1小时
    444008000: False,  # 暂停交易
    444016000: True,  # 停牌一天
}

suspension_config = {
    444001000: True,  # 上午停牌
    444002000: True,  # 下午停牌
    444003000: True,  # 今起停牌
    444004000: True,  # 盘中停牌
    444005000: True,  # 停牌半天
    444007000: True,  # 停牌1小时
    444008000: True,  # 暂停交易
    444016000: True,  # 停牌一天
}

if (Path(__file__).parent / "user_config.json").exists():
    data_path = read_datapath()
else:
    if "Windows" in platform.platform():
        data_path = r"D:\VS-Code-python\BBData_main\bin_data"
    else:
        data_path = r"/mnt/t/data/new_api_data"

(Path(data_path) / r"features").mkdir(exist_ok=True)
(Path(data_path) / r"datasets").mkdir(exist_ok=True)
(Path(data_path) / r"calendars").mkdir(exist_ok=True)
(Path(data_path) / r"instruments").mkdir(exist_ok=True)
