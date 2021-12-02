import datetime
import re
from .utils import get_time_millisecond, get_current_millisecond
from .log import log_error

# 输入各种格式字符，返回时间戳
def parse_time(text, last_time=0):
    text = str(text)
    d = _parse_current(text)
    if d > 0:
        return _ajust_parse_date(d, last_time)

    if not re.search(r'\d+', text):
        return 0

    d1 = _parse_x_year_y_month_z_day(text)
    if d1 > 0:
        return _ajust_parse_date(d1, last_time)

    d2 = _parse_x_y_z(text)
    if d2 > 0:
        return _ajust_parse_date(d2, last_time)

    d3 = _parse_x_month_y_day(text)
    if d3 > 0:
        return _ajust_parse_date(d3, last_time)

    d4 = _parse_x_y(text)
    if d4 > 0:
        return _ajust_parse_date(d4, last_time)
    d5 = _parse_txt(text)
    if d5 > 0:
        return _ajust_parse_date(d5, last_time)

    d6 = _parse_x__y__z(text)
    if d6 > 0:
        return _ajust_parse_date(d6, last_time)

    d7 = _parse_x__y(text)
    if d7 > 0:
        return _ajust_parse_date(d7, last_time)
    d8 = _timestamp(text)
    if d8 > 0:
        return _ajust_parse_date(d8, last_time)

    d9 = _parse_hour_minute_second(text)
    if d9 > 0:
        return _ajust_parse_date(d9, last_time)

    d10 = _parse_x___y___z(text)
    if d10 > 0:
        return _ajust_parse_date(d10, last_time)

    d11 = _parse_hour_minute(text)
    if d11 > 0:
        return _ajust_parse_date(d11, last_time)

    return 0

def _parse_hour_minute_second(text):
    try:
        m = re.search(r'(\d+):(\d+):(\d+)', text)
        if not m:
            return 0
        hour = int(m.group(1))
        minute = int(m.group(2))
        second = int(m.group(3))
        now = datetime.datetime.now()
        now = now.replace(hour=hour, minute=minute, second=second)
        return get_time_millisecond(now.timestamp())
    except Exception as ex:
        log_error(ex)
    return 0

def _parse_hour_minute(text):
    try:
        m = re.search(r'(\d+):(\d+)', text)
        if not m:
            return 0
        hour = int(m.group(1))
        minute = int(m.group(2))
        now = datetime.datetime.now()
        if 0 < hour > 24:
            return 0

        if 0 < minute > 60:
            return 0
        now = now.replace(hour=hour, minute=minute)
        return get_time_millisecond(now.timestamp())
    except Exception as ex:
        log_error(ex)
    return 0

def _timestamp(text):
    if len(str(text)) == 10 and text.isdigit():
        return get_time_millisecond(int(text))
    elif len(str(text)) == 13:
        return int(text)
    return 0

def _parse_after(text, year, month, day):

    d1 = _parse_x_hour_y_minute_z_second(text, year, month, day)
    if d1 > 0:
        return d1

    d2 = _parse_x_hour_y_minute(text, year, month, day)
    if d2 > 0:
        return d2

    d3 = _parse_x_hour_y_minute_z_second_ch(text, year, month, day)
    if d3 > 0:
        return d3

    d4 = _parse_x_hour_y_minute_ch(text, year, month, day)
    if d4 > 0:
        return d4

    hour = datetime.datetime.now().hour
    minute = datetime.datetime.now().minute
    second = datetime.datetime.now().second
    now = datetime.datetime(year, month, day, hour, minute, second)
    return get_time_millisecond(now.timestamp())

def _ajust_parse_date(current_time, last_time):
    if last_time > 0:
        return _check_last_time(current_time, last_time)
    return _check_last_time(current_time, get_current_millisecond())

def _check_last_time(current_time, last_time):

    current_date = datetime.datetime.fromtimestamp(current_time / 1000)

    if current_time >= get_current_millisecond():
        return get_current_millisecond()

    return get_time_millisecond(current_date.timestamp())

def _parse_x_year_y_month_z_day(text):
    try:
        m = re.search(r'(\d+)年(\d+)月(\d+)日', text)
        if not m:
            return 0
        year = int(m.group(1))
        month = int(m.group(2))
        day = int(m.group(3))
        if 1 < month > 12:
            return 0
        if 1 < day > 31:
            return 0
        if year < 100:
            year += 2000
        return _parse_after(text.split(m.group())[-1], year, month, day)

    except Exception as ex:
        log_error(ex)

def _parse_x_month_y_day(text):
    try:
        m = re.search(r'(\d+)月(\d+)日', text)
        if not m:
            return 0
        month = int(m.group(1))
        day = int(m.group(2))
        if 1 < month > 12:
            return 0
        if 1 < day > 31:
            return 0

        return _parse_after(text.split(m.group())[-1], datetime.datetime.now().year, month, day)
    except Exception as ex:
        log_error(ex)

def _parse_x_y_z(text):
    try:
        m = re.search(r'(\d+)-(\d+)-(\d+)', text)
        if not m:
            return 0
        year = int(m.group(1))
        month = int(m.group(2))
        day = int(m.group(3))
        if 1 < month > 12:
            return 0
        if 1 < day > 31:
            return 0
        if year < 100:
            year += 2000
        return _parse_after(text.split(m.group())[-1], year, month, day)

    except Exception as ex:
        log_error(ex)

def _parse_x_y(text):
    try:
        m = re.search(r'(\d+)-(\d+)', text)
        if not m:
            return 0
        month = int(m.group(1))
        day = int(m.group(2))
        if 1 < month > 12:
            return 0
        if 1 < day > 31:
            return 0
        return _parse_after(text.split(m.group())[-1], datetime.datetime.now().year, month, day)
    except Exception as ex:
        log_error(ex)

def _parse_x__y__z(text):
    try:
        m = re.search(r'(\d+)/(\d+)/(\d+)', text)
        if not m:
            return 0
        if len(str(m.group(3))) == 4:
            year = int(m.group(3))
            month = int(m.group(1))
            day = int(m.group(2))
        else:
            year = int(m.group(1))
            month = int(m.group(2))
            day = int(m.group(3))
        if 1 < month > 12:
            return 0
        if 1 < day > 31:
            return 0
        if year < 100:
            year += 2000
        return _parse_after(text.split(m.group())[-1], year, month, day)
    except Exception as ex:
        log_error(ex)

def _parse_x___y___z(text):
    try:
        m = re.search(r'(\d+)\.(\d+)\.(\d+)', text)
        if not m:
            return 0
        if len(str(m.group(3))) == 4:
            year = int(m.group(3))
            month = int(m.group(1))
            day = int(m.group(2))
        else:
            year = int(m.group(1))
            month = int(m.group(2))
            day = int(m.group(3))
        if 1 < month > 12:
            return 0
        if 1 < day > 31:
            return 0
        if year < 100:
            year += 2000
        return _parse_after(text.split(m.group())[-1], year, month, day)
    except Exception as ex:
        log_error(ex)

def _parse_x__y(text):
    try:
        m = re.search(r'(\d+)/(\d+)', text)
        if not m:
            return 0
        month = int(m.group(1))
        day = int(m.group(2))
        if 1 < month > 12:
            return 0
        if 1 < day > 31:
            return 0
        return _parse_after(text.split(m.group())[-1], datetime.datetime.now().year, month, day)
    except Exception as ex:
        log_error(ex)

def _parse_txt(text):
    try:
        m = re.search(r'(\d+)(\w+)前', text)
        if not m:
            return 0
        now = datetime.datetime.now()
        txt = m.group(2)

        if '秒' == txt:
            num = int(m.group(1))
            now = now - datetime.timedelta(seconds=num)
            return get_time_millisecond(now.timestamp())
        elif '分钟' == txt:
            num = int(m.group(1))
            now = now - datetime.timedelta(minutes=num)
            return get_time_millisecond(now.timestamp())
        elif '小时' == txt:
            num = int(m.group(1))
            now = now - datetime.timedelta(hours=num)
            return get_time_millisecond(now.timestamp())
        elif '天' == txt:
            num = int(m.group(1))
            now = now - datetime.timedelta(days=num)
            return get_time_millisecond(now.timestamp())
        elif '年' == txt:
            num = int(m.group(1))
            now = now - datetime.timedelta(days=num * 365)
            return get_time_millisecond(now.timestamp())
        return 0

    except Exception as ex:
        log_error(ex)

def _parse_current(text):
    try:
        if isinstance(text, str):
            text = text.strip()
            if '刚刚' == text or '刚才' == text:
                return get_time_millisecond(datetime.datetime.now().timestamp())
            elif '今天' in text:
                return _parse_after(text.split('今天')[-1], datetime.datetime.now().year,
                                        datetime.datetime.now().month,
                                        datetime.datetime.now().day)
            return 0
        else:
            return 0
    except Exception as ex:
        log_error(ex)

# 处理时分秒
def _parse_x_hour_y_minute_z_second(text, year, month, day):
    try:
        m = re.search(r'(\d+):(\d+):(\d+)', text)
        if not m:
            return 0

        hour = int(m.group(1))
        if '下午' in text:
            hour += 12
        minute = int(m.group(2))
        second = int(m.group(3))

        if 0 < hour > 24:
            return 0
        if 0 < minute > 60:
            return 0
        if 0 < second > 60:
            return 0

        now = datetime.datetime(year, month, day, hour, minute, second)
        return get_time_millisecond(now.timestamp())

    except Exception as ex:
        log_error(ex)

def _parse_x_hour_y_minute_z_second_ch(text, year, month, day):
    try:
        m = re.search(r'(\d+)：(\d+)：(\d+)', text)
        if not m:
            return 0

        hour = int(m.group(1))
        if '下午' in text:
            hour += 12
        minute = int(m.group(2))
        second = int(m.group(3))

        if 0 < hour > 24:
            return 0
        if 0 < minute > 60:
            return 0
        if 0 < second > 60:
            return 0

        now = datetime.datetime(year, month, day, hour, minute, second)
        return get_time_millisecond(now.timestamp())

    except Exception as ex:
        log_error(ex)

def _parse_x_hour_y_minute_ch(text, year, month, day):
    try:
        m = re.search(r'(\d+)：(\d+)', text)
        if not m:
            return 0
        hour = int(m.group(1))
        if '下午' in text:
            hour += 12
        minute = int(m.group(2))
        second = 0

        if 0 < hour > 24:
            return 0
        if 0 < minute > 60:
            return 0
        if 0 < second > 60:
            return 0

        now = datetime.datetime(year, month, day, hour, minute, second)
        return get_time_millisecond(now.timestamp())

    except Exception as ex:
        log_error(ex)

def _parse_x_hour_y_minute(text, year, month, day):
    try:
        m = re.search(r'(\d+):(\d+)', text)
        if not m:
            return 0
        hour = int(m.group(1))
        if '下午' in text:
            hour += 12
        minute = int(m.group(2))
        second = 0

        if 0 < hour > 24:
            return 0
        if 0 < minute > 60:
            return 0
        if 0 < second > 60:
            return 0

        now = datetime.datetime(year, month, day, hour, minute, second)
        return get_time_millisecond(now.timestamp())

    except Exception as ex:
        log_error(ex)


