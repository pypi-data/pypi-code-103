#!/usr/bin/python3
"""
DECIMAL TIME
============

About
=====
1 year = 10 months
1 week = 10 days
1 day = 10 hours
1 hour = 100 minutes
1 minute = 100 seconds

=> 1 second = 0.864 standard SI seconds.
=> 1 month = 3~4 weeks.

Years start at 1970 Jan 1, at UNIX time start date.
"""

import copy
import datetime
import calendar
import argparse
import time
import math

parser = argparse.ArgumentParser()
parser.add_argument('-s', '--show', help='Persist showing counting time.')

class Constants:
    origin_date = datetime.datetime(1970, 1, 1, 0, 0)
    year_length = 365
    month_lengths = [36, 37] * 5
    second_length = 0.864

constant = Constants()


class Date:

    def __init__(self, *args):

        self.origin = constant.origin_date

        if args:
            if isinstance(args[0], datetime.datetime):
                self.date = args[0]
                self.compute_date()
            else:
                self.interpret_date(*args)
        else:
            self.interpret_date(0, 0, 0)

    @classmethod
    def utcnow(cls):
        date = datetime.datetime.utcnow()
        return Date(date)

    @classmethod
    def from_day(cls, day):
        """
            Takes: offset from constant.origin in days (fractional)
            Returns: Date object
        """
        delta = datetime.timedelta(days=day)
        date = constant.origin_date + delta
        return Date(date)

    @classmethod
    def datetime(cls, *args):
        date = datetime.datetime(*args)
        return Date(date)

    def compute_date(self):
        """
            Takes:
            (self.date - the Gregorian date)

            Sets:
            (self.year, self.month, self.day, self.hour, self.minute, self.second,

            self.yday - day of the year
            self.tseconds - decimal seconds today,
            self.seconds - decimal unix seconds)
        """
        self.year = (self.date.year - self.origin.year)
        self.yday = self.date.timetuple().tm_yday
        self.month = self.set_month()
        self.day = self.yday - sum(self.month_lengths[:self.month][:-1]) \
            or self.month_lengths[self.month]

        self.tseconds = self.get_day_seconds() / constant.second_length
        self.hour = int(self.tseconds/10000.)
        self.minute = int((self.tseconds - self.hour*10000.) / 100.)
        self.second = self.tseconds - (self.hour*10000. + self.minute*100)

        # Unix dseconds
        self.seconds = time.mktime(self.date.timetuple()) / constant.second_length

    def interpret_date(self, year, month=1, day=1, hour=0, minute=0, second=0.):
        """
            Takes:
            (self.year, self.month, self.day, self.hour, self.minute, self.second)

            Sets:
            (self.date, self.seconds - unix decimal seconds)

        """
        year = int(year)
        years = abs(year)
        months = min(10, max(0, int(month - 1)))
        days = min(38, max(0, int(day - 1)))
        hours = min(10, max(0, int(hour)))
        minutes = min(100, max(0, int(minute)))
        seconds = min(100., max(0., second))

        if seconds == float(100):
            seconds = 0.
            minutes += 1

        # Starting total decimal seconds computation
        self.seconds = 0.

        leaps = max(0, (abs(year)+1) // 4)
        full_year_days = (years*365 + leaps)

        self.month_lengths = constant.month_lengths
        if (year + 2) % 4 == 0:
            self.month_lengths[-1] = 38
        else:
            days = min(37, days)

        self.yday = sum(self.month_lengths[:months] + [days])
        self.tseconds = hours * 10000 + minutes * 100 + seconds

        self.seconds += (full_year_days + self.yday) * 100000 + self.tseconds

        if year < 0:
            self.seconds = -self.seconds

        self.date = datetime.datetime.utcfromtimestamp(self.seconds * constant.second_length)

        # set attributes (or could call self.compute_date() now, cause having self.date)
        self.year = year
        self.month = months + 1
        self.day = days + 1
        self.hour = hours
        self.minute = minutes
        self.second = seconds


    def get_time_delta(self):
        self.delta = self.date - self.origin

    def set_month(self):
        for i, month_length in enumerate(self.set_month_lengths()):
            if sum(self.month_lengths[:i+1]) >= self.yday:
                break
        return i+1

    def get_year_length(self):
        year_length = constant.year_length

        if calendar.isleap(self.date.year):
            year_length += 1
        self.year_length = year_length
        return self.year_length

    def set_month_lengths(self):

        if calendar.isleap(self.date.year):
            self.month_lengths = copy.copy(constant.month_lengths)
            self.month_lengths[-1] = 38 # leap year last month length
            return self.month_lengths
        else:
            self.month_lengths = copy.copy(constant.month_lengths)
            return self.month_lengths

    def get_unix_seconds(self):
        self.get_time_delta()
        return self.delta.total_seconds()

    def get_day_seconds(self):
        midnight = self.date.replace(hour=0, minute=0, second=0, microsecond=0)
        return (self.date - midnight).total_seconds()

    @property
    def weekday(self):
        # We assume that 00000-01-01 was "1st" day of week, denoted as "0"
        return math.floor(self.seconds / 100000.) % 10

    @property
    def week(self):
        days = (self.yday - self.weekday)
        if days <= 0:
            weeks = 1
        else:
            weeks = int(math.ceil(days / 10.)) + 1

        return weeks

    def isoformat(self, round_secs=False):
        return '{:04d}-{:02d}-{:02d}T{:02d}:{:02d}:{}'.format(
            self.year, self.month, self.day,
            self.hour, self.minute, self.second
        )

    @property
    def daet(self):
        'date'
        return '{:04d}-{:02d}-{:02d}'.format(self.year, self.month, self.day)

    @property
    def daey(self):
        'absolute week-time since 1970-01-01 00:00:00'
        diff = (self.date - constant.origin_date).total_seconds()

        return diff/86400.

    @property
    def saec(self):
        'decimal second of the day'
        return self.hour*10000 + self.minute*100 + self.second

    @property
    def waek(self):
        return self.daey / 10.

    @property
    def taem(self, round_secs=True):
        'time'
        secs = math.floor(self.second)
        mils = str(self.second - secs).split('.', 1)[-1]

        if round_secs:
            return '{:02d}:{:02d}:{:02d}'.format(self.hour, self.minute, secs)

        else:
            return '{:02d}:{:02d}:{:02d}.{}'.format(self.hour, self.minute, secs, mils)

    @property
    def show(self):
        return f'{self.daet} {self.taem}'

    def __repr__(self):
        return f'detime.detime({self.year}, {self.month}, {self.day}, {self.hour}, {self.minute}, {self.second})'

detime = Date


def counter():
    args = parser.parse_args()

    if args.show == 'how':

        while True:
            tm = time.gmtime()
            date = detime.utcnow()
            print("[{:04d}-{:02d}-{:02d} =] {} [= {:02d}:{:02d}:{:02d}]".format(
                tm.tm_year, tm.tm_mon, tm.tm_mday, date.show, tm.tm_hour, tm.tm_min, tm.tm_sec
            ), end='\r', flush=True)
            del date
            time.sleep(0.1)

    else:
        tm = time.gmtime()
        t = detime.utcnow()
        print(f'{t.daet} [{t.weekday}] @{t.taem}')


if __name__ == '__main__':
    counter()
