# -*- coding: utf-8 -*-
import re
import datetime
import math
import os
import sys
import traceback
from common import pyetc
from common import db
from common import define
from datetime import datetime as dtime
from common.define import (MARKET)
import os
# 交易日期类型
TRADE_DATE_TYPE = define.enum(month=0, quarter=1, halfyear=2)

def atoi(s):
    try:
        return int(s)
    except Exception as e:
        #print(e)
        return 0

def format_traceback():
    lines = []
    lines.extend(traceback.format_stack())
    lines.extend(traceback.format_tb(sys.exc_info()[2]))
    lines.extend(traceback.format_exception_only(sys.exc_info()[0], sys.exc_info()[1]))

    join_line = ["Traceback (most recent call last):\n"]
    for strg in lines:
        if not isinstance(strg, str):
            join_line.append(strg.decode("utf8"))
        else:
            join_line.append(strg)

    except_str = ''.join(join_line)

    # Removing the last \n
    except_str = except_str[:-1]
    return except_str

def gen_path(STOCK_CODE_PATH):
    if getattr(sys, 'frozen', False):
        pathname = STOCK_CODE_PATH
    else:
        pathname = os.path.join(os.path.dirname(os.path.dirname(__file__)), STOCK_CODE_PATH)
    return pathname

def format_datetime(datetime:str):
    length = len(str(datetime))
    if length == 17:
        return "%s-%s-%s %s:%s:%s.%s" % (
             datetime[:4], datetime[4:6], datetime[6:8], datetime[8:10], datetime[10:12], datetime[12:14], datetime[14:]
        )
    elif length == 9:
        return "%s:%s:%s.%s"% (datetime[0:2],datetime[2:4],datetime[4:6],datetime[6:])
    else:
        return

# 方便兼容打包exe
def get_path_dirname():
    if getattr(sys, 'frozen', False):
        application_path = os.path.dirname(sys.executable)
    else:
        # 取当前脚本的上级目录
        application_path = os.path.dirname(os.path.dirname(__file__))
    return application_path


def get_db_info():
    path = "conf" + os.sep + "db.conf"
    work_dir = get_path_dirname()
    full_path = work_dir + os.sep + path

    setting = pyetc.load(full_path)
    return setting.db_info


def get_strategy_setting():
    path = "conf" + os.sep + "Strategy_conf.py"
    work_dir = get_path_dirname()
    full_path = work_dir + os.sep + path

    setting = pyetc.load(full_path)
    return setting

def get_strategy_conf():
    path = ["conf","strategy_stk","stk.xlsx"]
    path = os.sep.join(path)
    work_dir = get_path_dirname()
    full_path = work_dir + os.sep + path

    import xlrd
    # 1、打开文件
    with xlrd.open_workbook(full_path) as f:
        sheet = f.sheet_by_index(0)
        codes =sheet.col_values(0)

    return codes


def create_database(info=None, table=''):
    if not info:
        info = get_db_info()
    print("connect %s"%info['host'])
    return db.DB(host=info['host'], user=info['user'], passwd=info['password'], db=info['db'], table=table, charset=info['charset'],
                 port=info['port'])


def make_date(date_str):
    if date_str == '--': return 0
    date_arr = date_str.split('-')

    if len(date_arr) == 3:
        return int(date_arr[0]) * 10000 + int(date_arr[1]) * 100 + int(date_arr[2])
    return None


def get_number(str):
    if str == '--':    return 0
    m = re.match('(-{0,1}\d+\.{0,1}\d*).*', str)
    if m:
        return float(m.groups()[0])
    else:
        return 0


def get_bignumber(str):
    if str == '--':    return 0
    m = re.match('(-{0,1}\d+[,\d+]*\.{0,1}\d*).*', str)
    if m:
        return float(m.groups()[0].replace(',', ''))
    else:
        return 0


def parse_tds(trs):
    tds = trs.findAll("td")
    return [tdc.text for tdc in tds]


# 找不同
def find_diff(base, iters):
    return [s for s in iters if s not in base]


# 向前获取最近的财报日期
# date_type： 0：月报；1：季报；2：半年报
def get_pre_date_nearby(datetime, date_type=TRADE_DATE_TYPE.quarter):
    date_range = [131, 230, 331, 430, 531, 630, 731, 831, 930, 1031, 1130, 1231]
    if TRADE_DATE_TYPE.quarter == date_type:
        date_range = [331, 630, 930, 1231]
    elif TRADE_DATE_TYPE.halfyear == date_type:
        date_range = [630, 1231]

    mmdd = datetime % 10000
    yyyy = datetime // 10000
    calc_datetime = 0
    for d in date_range[::-1]:
        # if mmdd > d+100: # 因为季报推迟1个月才会公布。
        if mmdd > d:
            calc_datetime = d
            break
    if calc_datetime == 0:
        # calc_datetime =  date_range[-1]  if mmdd/100>2 else date_range[-2] # 因为季报推迟1个月才会公布。
        calc_datetime = date_range[-1:][0]
        yyyy -= 1
    return yyyy * 10000 + calc_datetime


def get_last_year_finance_report_date(datetime):
    dates = []
    date_range = [1231, 930, 630, 331]
    pre_date = get_pre_date_nearby(datetime)
    dates.append(pre_date)
    md = pre_md = pre_date % 10000
    year = pre_y = pre_date / 10000
    beg_index = date_range.index(pre_md)
    for index in range(len(date_range)):
        beg_index += 1
        if beg_index == len(date_range):
            beg_index = 0
            year -= 1
        md = date_range[beg_index]
        if md == pre_md: break
        dates.append(year * 10000 + md)
    return dates


# 向后获取最近的日期
def get_next_date_nearby(datetime, date_type=TRADE_DATE_TYPE.quarter):
    date_range = [131, 230, 331, 430, 531, 630, 731, 831, 930, 1031, 1130, 1231]
    if TRADE_DATE_TYPE.quarter == date_type:
        date_range = [331, 630, 930, 1231]
    elif TRADE_DATE_TYPE.halfyear == date_type:
        date_range = [630, 1231]

    mmdd = datetime % 10000
    yyyy = datetime / 10000
    calc_datetime = 0
    for d in date_range:
        if mmdd < d:
            calc_datetime = d
            break

    if calc_datetime == 0:
        calc_datetime = date_range[0]
        yyyy += 1
    return yyyy * 10000 + calc_datetime


# def get_offset_datetime(dt, offset):  # 得到以dt为基准日往前(后)偏差的日期  offset负为往前
#     base_day = datetime.datetime(dt // 10000, dt // 100 % 100, dt % 100)
#     return int((base_day + datetime.timedelta(offset)).strftime('%Y%m%d'))

def get_offset_datetime(dt, offset):
    """得到以dt为基准日往前(后)偏差的日期  offset负为往前.根据时间传参判断偏移计算单位"""
    from dateutil.parser import parse
    dt_star = parse(str(dt))
    type_ = get_datetime_type(dt)
    if type_ == "minutes":
        date = dt_star+datetime.timedelta(minutes=offset)
        return int(date.strftime('%Y%m%d%H%M'))
    elif type_ == "day":
        date = dt_star + datetime.timedelta(days=offset)
        return  int(date.strftime('%Y%m%d'))
    else:
        print("获取时间类型异常")

def get_days_interval(a_dt, b_dt):  # 获取两个交易日偏差多少天
    a_day = datetime.datetime(a_dt // 10000, a_dt // 100 % 100, a_dt % 100)
    b_day = datetime.datetime(b_dt // 10000, b_dt // 100 % 100, b_dt % 100)
    timedelta = a_day - b_day
    return abs(timedelta.days)


def get_week_day(a_dt):  # 星期几
    a_day = datetime.datetime(a_dt / 10000, a_dt / 100 % 100, a_dt % 100)
    return a_day.weekday() + 1


def get_avarage(datas):  # 获取平均数
    if not datas or len(datas) == 0: return 0
    total = 0
    for data in datas:
        total += data
    return total / float(len(datas))


def get_variance(datas):
    if not datas or len(datas) == 0: return 0
    avarage = get_avarage(datas)
    total = 0
    for data in datas:
        total += (data - avarage) * (data - avarage)
    return total / float(len(datas))


def get_standard_deviation(datas):
    if not datas or len(datas) == 0: return 0
    variance = get_variance(datas)
    return math.sqrt(variance)


def is_trade_local_time(now_time):
    hhmm = now_time % 10000
    weekday = datetime.date.today().weekday()
    if weekday == 5 or weekday == 6: return False
    return True


def is_trading_time(hhmm :int, market:MARKET):    
    if market == MARKET.stock or market == MARKET.option:
        if hhmm >= 928 and hhmm <= 1132: return True
        if hhmm >= 1258 and hhmm <= 1502: return True
    elif market == MARKET.future:
        if hhmm >= 928 and hhmm <= 1132: return True
        if hhmm >= 1258 and hhmm <= 1502: return True
        if hhmm >= 2058 and hhmm <= 2400: return True
        if hhmm >= 0 and hhmm <= 300: return True
    return False


def gen_datetime_range(beg, end, delta):
    datetime_list=[]
    interval = get_days_interval(beg, end)

    if interval <= delta:
        datetime_list.append((beg, end))
        return datetime_list

    list_num = interval//delta+1
    for n in range(list_num):
        _beg = get_offset_datetime(beg, delta*n)
        _end = get_offset_datetime(beg, delta*(n+1)-1)
        _end = _end if _end < end else end
        datetime_list.append((_beg,_end))

    return datetime_list

def get_datetime_type(datetime):
    import math
    len = int(math.log10(datetime))+1
    _type={ 8:"day",
            12:"minutes",
            9:"tick"}
    return _type[len]

def strptime(datetime):
    _t = get_datetime_type(datetime)
    if _t == "day": datetime *=10000
    if isinstance(datetime, int):
        _dt = str(datetime)
    else:
        _dt = datetime
    return dtime.strptime(_dt, '%Y%m%d%H%M')


def calc_time_diff(beg, end=None):
    b = datetime.datetime.strptime(str(beg), '%Y%m%d%H%M%S%f')
    if end:
        e = datetime.datetime.strptime(str(end), '%Y%m%d%H%M%S%f')
    else:
        e = datetime.datetime.now()
    seconds_diff = (e - b).total_seconds()
    return seconds_diff


def gen_new_time(beg,**kwargs):
    beg = str(beg)
    beg = datetime.datetime.strptime(beg, "%H%M%S%f")
    # print(times1)
    new_time = int((beg + datetime.timedelta(**kwargs)).strftime('%H%M%S%f')[:-3])
    return new_time


def varname(p):
    """获取变量名字的字符串"""
    import inspect, re
    for line in inspect.getframeinfo(inspect.currentframe().f_back)[3]:
        m = re.search(r'\bvarname\s*\(\s*([A-Za-z_][A-Za-z0-9_]*\.)*([A-Za-z_][A-Za-z0-9_]*)\s*\)', line)
    if m: return m.group(2)


def reduce_mem_usage(props):
    import numpy as np

    """收缩DataFrame 内存，类型自动向下转换"""
    # 计算当前内存
    start_mem_usg = props.memory_usage().sum() / 1024 ** 2
    print("Memory usage of the dataframe is :", start_mem_usg, "MB")

    # 哪些列包含空值，空值用-999填充。why：因为np.nan当做float处理
    NAlist = []
    for col in props.columns:
        # 这里只过滤了objectd格式，如果你的代码中还包含其他类型，请一并过滤
        if (props[col].dtypes != object):

            print("**************************")
            print("columns: ", col)
            print("dtype before", props[col].dtype)

            # 判断是否是int类型
            isInt = False
            mmax = props[col].max()
            mmin = props[col].min()

            # Integer does not support NA, therefore Na needs to be filled
            if not np.isfinite(props[col]).all():
                NAlist.append(col)
                props[col].fillna(-999, inplace=True)  # 用-999填充

            # test if column can be converted to an integer
            asint = props[col].fillna(0).astype(np.int64)
            result = np.fabs(props[col] - asint)
            result = result.sum()
            if result < 0.01:  # 绝对误差和小于0.01认为可以转换的，要根据task修改
                isInt = True

            # make interger / unsigned Integer datatypes
            if isInt:
                if mmin >= 0:  # 最小值大于0，转换成无符号整型
                    if mmax <= 255:
                        props[col] = props[col].astype(np.uint8)
                    elif mmax <= 65535:
                        props[col] = props[col].astype(np.uint16)
                    elif mmax <= 4294967295:
                        props[col] = props[col].astype(np.uint32)
                    else:
                        props[col] = props[col].astype(np.uint64)
                else:  # 转换成有符号整型
                    if mmin > np.iinfo(np.int8).min and mmax < np.iinfo(np.int8).max:
                        props[col] = props[col].astype(np.int8)
                    elif mmin > np.iinfo(np.int16).min and mmax < np.iinfo(np.int16).max:
                        props[col] = props[col].astype(np.int16)
                    elif mmin > np.iinfo(np.int32).min and mmax < np.iinfo(np.int32).max:
                        props[col] = props[col].astype(np.int32)
                    elif mmin > np.iinfo(np.int64).min and mmax < np.iinfo(np.int64).max:
                        props[col] = props[col].astype(np.int64)
            else:  # 注意：这里对于float都转换成float16，需要根据你的情况自己更改
                props[col] = props[col].astype(np.float16)

            print("dtype after", props[col].dtype)
            print("********************************")
    print("___MEMORY USAGE AFTER COMPLETION:___")
    mem_usg = props.memory_usage().sum() / 1024 ** 2
    print("Memory usage is: ", mem_usg, " MB")
    print("This is ", 100 * mem_usg / start_mem_usg, "% of the initial size")
    return props, NAlist


# 获得第几季度
def get_quarter(datetime):
    quarter_range = [331,630,930,1231]
    mm_dd = datetime%10000
    for idx,quarter_ in enumerate(quarter_range):
        if mm_dd<=quarter_:
            return  idx+1
    print("get_quarter err")