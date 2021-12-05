from datetime import datetime
from datetime import timedelta
import pandas as pd
import UtilTools.FrequencyUtils as FrequencyUtils
from dateutil.relativedelta import relativedelta

def convertDateStrToDatetime(dateStr):
    if isinstance(dateStr,pd.Timestamp):
        return dateStr.to_datetime()
    if isinstance(dateStr,datetime):
        return dateStr.replace(microsecond=0)
    if len(dateStr) == len('2016-01-01'):
        return datetime.strptime(dateStr,'%Y-%m-%d')
    elif len(dateStr) == len('2016-01-01 00:00:00'):
        return datetime.strptime(dateStr,'%Y-%m-%d %H:%M:%S')
    elif len(dateStr) == len('2016-01-01 00:00'):
        return datetime.strptime(dateStr,'%Y-%m-%d %H:%M')
    elif len(dateStr) == len('20160101'):
        return datetime.strptime(dateStr,'%Y%m%d')
    elif len(dateStr) == len('20160101 00:00:00'):
        return datetime.strptime(dateStr,'%Y%m%d %H:%M:%S')
    elif len(dateStr) == len('2018-08-20T10:00:00Z'):
        return datetime.strptime(dateStr,'%Y-%m-%dT%H:%M:%SZ')
    else:
        raise Exception("Date Format is invalid")
    return dateStr

def convertDateToTheTradeStart(dateStr):
    if isinstance(dateStr,datetime):
        date = dateStr
    else:
        date = convertDateStrToDatetime(dateStr)
    date = date.replace(hour=9, minute=0, second=0)
    return date

def convertDateToTheTradeEnd(dateStr):
    if isinstance(dateStr,datetime):
        date = dateStr
    else:
        date = convertDateStrToDatetime(dateStr)
    date = date.replace(hour=23,minute=30,second=0)
    return date

def convertDateToStr(date):
    if isinstance(date, datetime):
        return date.strftime('%Y-%m-%d')
    return date

def convertTimestampToStr(timestmap):
    if isinstance(timestmap,pd.Timestamp):
        return timestmap.strftime('%Y-%m-%d %H:%M:%S')
    if isinstance(timestmap,datetime):
        return timestmap.strftime('%Y-%m-%d %H:%M:%S')
    return timestmap

def getTodayStr():
    return datetime.now().strftime('%Y-%m-%d')

def getLastOneYearDate():
    today = getTodayStr()
    oneYearBefore = getNMonthBeforDateStr(today,12)
    return (oneYearBefore,today)

def getNMonthBeforDateStr(monthNum):
    today = getToday()
    delta = relativedelta(months=monthNum)
    before =  today - delta
    return before.strftime('%Y-%m-%d')

def getNMonthBeforDateStr(dateStr,monthNum):
    today = datetime.strptime(dateStr,'%Y-%m-%d')
    delta = relativedelta(months=monthNum)
    before =  today - delta
    return before.strftime('%Y-%m-%d')

def getMacdStartDate(dateStr,freq):
    orginDate = convertDateStrToDatetime(dateStr)
    count = 33
    timeDiff = timedelta(days=1)
    if freq == FrequencyUtils.TradeType.D:
        timeDiff = timedelta(days=1)
    elif freq == FrequencyUtils.TradeType.W:
        timeDiff = timedelta(days=7)
    elif freq == FrequencyUtils.TradeType.M:
        timeDiff = timedelta(days=31)
    elif freq == FrequencyUtils.TradeType.Sixty:
        count = count / 4
    elif freq == FrequencyUtils.TradeType.Thirty:
        count = count / 8
    elif freq == FrequencyUtils.TradeType.Fifteen:
        count = count / 16
    elif freq == FrequencyUtils.TradeType.Five or freq == FrequencyUtils.TradeType.One:
        count = 1
    macdDate = orginDate - count * timeDiff * 2
    return macdDate

def getDayDiff(date1,date2):
    date1 = convertDateStrToDatetime(date1)
    date2 = convertDateStrToDatetime(date2)
    return (date2 - date1).days

def convertDateToPaht(date):
    return date.strftime('%Y_%m_%d')

def getNow():
    return datetime.now()

def getToday():
    now = datetime.now()
    today = datetime(now.year,now.month,now.day)
    return today

def getLastTradeDayStr():
    today = getToday()
    timeDiff = timedelta(days=1)
    if datetime.now().hour < 9:
        today = today - timeDiff
    if today.isoweekday() <= 5:
        return today.strftime('%Y-%m-%d')
    else:
        yesterday = today - timeDiff
        while yesterday.isoweekday() > 5:
            yesterday = yesterday - timeDiff
        return yesterday.strftime('%Y-%m-%d')

def getNMonthBeforDate(monthNum):
    today = getToday()
    delta = relativedelta(months=monthNum)
    return  today - delta

def isDateExceedNMonth(startDate,monthNum):
    today = getToday()
    delta = relativedelta(months=monthNum)
    startDate = convertDateStrToDatetime(startDate)
    if startDate >= today - delta:
        return False
    return True

def convertTimeToDate(date):
    assert isinstance(date,datetime)
    dayDate = datetime(date.year,date.month,date.day)
    return dayDate




