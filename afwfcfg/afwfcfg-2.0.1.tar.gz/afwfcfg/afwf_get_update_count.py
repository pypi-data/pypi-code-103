#!/usr/bin/env python
# coding=utf-8

from datetime import datetime
from datetime import timedelta
from afwfcfg.afwf_log import *

"""
 功能描述:afwf模块更新量统计
    参数:time_start, 统计开始的时间，YYYYMMDDHH
         period,     统计从指定开始时间之后的小时数
         proccess,   统计进程名称，为local_update或online_update
   返回值:在指定的时间范围内更新的总条数
     说明:时间需要取合理的范围，最好不超过一年
"""


def AFWF_GetUpdateCount(time_start, period, proccess):
    query_time_start = datetime.strptime(time_start, '%Y%m%d%H')
    query_time_end = query_time_start + timedelta(hours=period)
    cnt = 0
    file_num = (query_time_end.date() - query_time_start.date()).days + 1
    for i in range(0, file_num):
        log_file = '/opt/afwf/logs/%s_%s.log' % (proccess, (query_time_start.date() + timedelta(days=i)).strftime('%Y%m%d'))

        if os.path.exists(log_file) is False:
            continue
        try:
            with open(log_file, 'r') as fp:
                for line in fp:
                    time_str = '%s-%s' % (line.split()[0], line.split()[1])
                    my_time = datetime.strptime(time_str, '%Y%m%d-%H:%M:%S')
                    if line.split()[3] != 'Success':
                        continue
                    if query_time_start < my_time < query_time_end:
                        cnt += int(line.split()[7])
        except Exception as e:
            AFWF_Error('Failed to get the update count. Reason:%s' % e)

    return cnt


if __name__ == '__main__':
    totalCnt = 0
    for hour in range(0, 24):
        cnt = AFWF_GetUpdateCount('20170705%s' % hour, 1, 'online_update')
        print(hour, ' Total: ', cnt)
        totalCnt += cnt
    print('Total all: ', totalCnt)
