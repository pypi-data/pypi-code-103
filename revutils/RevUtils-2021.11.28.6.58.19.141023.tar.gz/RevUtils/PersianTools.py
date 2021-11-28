from . import IO
from . import General
from datetime import datetime

import bs4

holiday_last_check_datetime = datetime(1, 1, 1)
holiday_last_result = False


def is_today_holiday():
    global holiday_last_result, holiday_last_check_datetime
    if General.dt_now().day != holiday_last_check_datetime.day:
        data = IO.get_url_utf8(url='https://www.time.ir')
        bs = bs4.BeautifulSoup(markup=data, features="html.parser")
        data = bs.find(name='div', attrs={'class': 'today'})
        data = data.find(name='div', attrs={'class': 'holiday'})
        holiday_last_result = False if data is None else True
        holiday_last_check_datetime = General.dt_now()
    return holiday_last_result
