from datetime import datetime
from howitzer.util.constants import EPOCH


def shortMonthString(month: int):
    shortMonthStrings = [
        "Jan",
        "Feb",
        "Mar",
        "Apr",
        "May",
        "Jun",
        "Jul",
        "Aug",
        "Sep",
        "Oct",
        "Nov",
        "Dec",
    ]
    return shortMonthStrings[month-1]


def shortStringFormat(date: datetime):
    return str(date.day) + shortMonthString(date.month) + str(date.year)


def unixMillis(dt: datetime):
    dt.replace(dt.replace(tzinfo=None))
    return (dt - EPOCH).total_seconds() * 1000.0
