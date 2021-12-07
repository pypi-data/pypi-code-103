#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 19/11/26 13:55
# @Author  : oujianhua
# @mail  : ojhtyy@163.com
# @File    : timeHelper.py
import datetime


#获取下次工作的秒数
from log import logger

#获取下个工作时间的秒数， 如当前时间是10:10:1 点 要获取 20点， 则取现在当天的20点的秒差， 要获取5点 ，则是获取现在到下一天的秒差
def getSleepSec(workHour):
    nowHour=datetime.datetime.now().hour
    #睡眠时长 ： 如果 现在未过当天的处理时间， 则当天处理， 如果现在已经过了处理时间，则明天处理
    nextWorkHour=workHour if nowHour<workHour else 24 + workHour
    nextWorkHourTimeForMat = datetime.datetime.strptime(str(datetime.date.today()), '%Y-%m-%d') + datetime.timedelta(seconds=nextWorkHour * 60 * 60 + 10)
    sleepSecond = round((nextWorkHourTimeForMat - datetime.datetime.now()).total_seconds())
    logger.info('sleep %s s ,next run time is %s ' % (str(sleepSecond), str(nextWorkHourTimeForMat)))
    return sleepSecond

if __name__=='__main__':
    getSleepSec(10)