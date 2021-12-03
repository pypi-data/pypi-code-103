import datetime
import calendar
from dateutil.relativedelta import relativedelta, TH, MO


class Holiday(datetime.datetime):
    THANKSGIVING = "thanksgiving"
    CHRISTMAS = "christmas"
    NEW_YEARS = "newyears"
    INDEPENDENCE = "independence"
    MEMORIAL = "memorial"
    LABOR = "labor"

    def __new__(cls, holiday_in):
        year = datetime.datetime.now().year
        holiday = holiday_in.lower()

        if holiday == Holiday.THANKSGIVING:
            # fourth thursday in November
            month = 11
            november = datetime.datetime(year=year, month=month, day=1)
            day = (november + relativedelta(day=31, weekday=TH(-1))).day
        elif holiday == Holiday.CHRISTMAS:
            month = 12
            day = 25
        elif holiday == Holiday.NEW_YEARS or holiday == "new years":
            month = 1
            day = 1
        elif holiday == Holiday.INDEPENDENCE:
            month = 7
            day = 4
        elif holiday == Holiday.MEMORIAL:
            month = 5
            day = 31
        elif holiday == Holiday.LABOR:
            # first monday in September
            month = 9
            november = datetime.datetime(year=year, month=month, day=1)
            day = (november + relativedelta(day=1, weekday=MO(1))).day
        else:
            raise RuntimeError("{} is not a recognised Holiday".format(holiday))
        return super().__new__(cls, year=year, month=month, day=day)


def is_weekend(dt):
    return dt.weekday() >= 5


def time_diff_to_str(diff, short=False, show_seconds=False):
    """
    Converts the difference to a string
    :param diff: the time difference to convert
    :param short: represent it as #d #h #m #s as opposed to # days # hours # minutes # seconds
    :param show_seconds: show the string including seconds (note if diff < 1 minute, seconds will be diplayed
    :return: the time difference as a string
    """
    days, remainder = divmod(diff.total_seconds(), 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes, seconds = divmod(remainder, 60)
    days = int(days)
    hours = int(hours)
    minutes = int(minutes)
    seconds = int(seconds)
    rtn = ''

    if days > 0:
        rtn += '{}{}{} '.format(days, 'd' if short else ' day', 's' if days > 1 and not short else '')
    if hours > 0:
        rtn += '{}{}{} '.format(hours, 'h' if short else ' hour', 's' if minutes > 1 and not short else '')
    if minutes > 0:
        rtn += '{}{}{} '.format(minutes, 'm' if short else ' minute', 's' if minutes > 1 and not short else '')
    if show_seconds or days == 0 and hours == 0 and minutes == 0 and seconds > 0:
        rtn += '{}{}{} '.format(seconds, 's' if short else ' second', 's' if seconds > 1 and not short else '')
    return rtn
