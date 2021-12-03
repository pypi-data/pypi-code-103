from datetime import datetime as dt
from datetime import timedelta as td
from dateutil import relativedelta as rd


class MovingWindow:
    def IterateWindow(self, traj, window_dates, func):
        pass


class Timespan(object):
    """An base class for either TimespanUnits or TimeSpans. Represents a window of time
    where the starting datetime is less than, or equal to the ending
    datetime."""

    def __init__(self):
        """ Timepsan constructor is meant to be overridden in subclasses"""
        self._start = dt.utcnow()
        self._end = dt.utcnow()

    def length_timedelta(self):
        # Return the datetime.timedelta between the two datetimes
        return self._end - self._start

    # Return the length of the timespan in seconds
    def length_timespan_seconds(self):
        return self.length_timedelta().total_seconds()

    def slide(self, timespan, amount=1):
        """ Slide the current timespan forward by the timespan amount. If the timespan object is a TimespanCustom
        type then the numtimes is in seconds"""
        self._start = timespan.add_time(self._start, amount)
        self._end = timespan.add_time(self._end, amount)

    @classmethod
    def add_time(cls, input_date, amount):
        """ Needs to be overridden in the implementing subclass for this function to do anything useful
        """
        pass


class TimespanUnit(Timespan):
    """ A Timepsan but that has a fundamental unit of measure (e.g., seconds, minutes, hours, days, weeks, months,
     years, etc."""

    def __init__(self, start, length=1):
        super().__init__()
        self.length = length
        self.start = start
        self.end = self.add_time(start, length)

    @classmethod
    def add_time(cls, input_date, amount):
        super().add_time(input_date, amount)

    def round_forwards(self):
        # Round backwards, then add a full X unit to the rounded time
        self.start = self.round_time_backwards(self.start)
        self.start = self.add_time(self.start, 1)
        self.end = self.add_time(self.start, 1)
        for i in range(1, self.length-1):
            self.end = self.add_time(self.end, 1)

    def round_backwards(self):
        # Round backwards, then add a full X unit to the rounded time
        self.start = self.round_time_backwards(self.start)
        self.end = self.add_time(self.start, 1)
        for i in range(1, self.length-1):
            self.end = self.add_time(self.end, 1)

    def getLength(self):
        """ return the length of the timespanunit in units"""
        return self.length

    @classmethod
    def round_time_forwards(cls, input_dt):
        # Round backwards, then add a full unit to the rounded time
        d1 = cls.round_time_backwards(input_dt)
        return cls.add_time(d1, 1)

    @classmethod
    def round_time_backwards(cls, input_dt):
        """Function will adjust the time window so that the start aligns with the earlier, whole TimespanUnit
                 unit of measure."""
        pass


class Timespan_Second(TimespanUnit):
    """A timespan represented in units seconds"""

    @classmethod
    def add_time(cls, input_date, amount):
        super().add_time(input_date, amount)
        return input_date + rd.relativedelta(seconds=+amount)

    @classmethod
    def round_time_backwards(cls, input_dt):
        """
        :param input_dt: the time to round to earliest second
        :return: datetime
        """
        super().round_time_backwards(input_dt)
        return input_dt - td(microseconds=input_dt.microsecond)


class Timespan_Minute(TimespanUnit):
    """A timespan represented in minutes"""

    @classmethod
    def add_time(cls, input_date, amount):
        super().add_time(input_date, amount)
        return input_date + rd.relativedelta(minutes=+amount)

    @classmethod
    def round_time_backwards(cls, input_dt):
        """
        :param input_dt: the time to round to earliest minute
        :return: datetime
        """
        super().round_time_backwards(input_dt)
        # round seconds to the nearest minute
        return input_dt - td(seconds=input_dt.second,
                             microseconds=input_dt.microsecond)


class Timespan_Hour(TimespanUnit):
    """A timespan represented in hours"""

    @classmethod
    def add_time(cls, input_date, amount):
        super().add_time(input_date, amount)
        return input_date + rd.relativedelta(hours=+amount)

    @classmethod
    def round_time_backwards(cls, input_dt):
        """
        :param input_dt: the time to round backwards
        :return: datetime
        """
        super().round_time_backwards(input_dt)
        # round minutes to the nearest hour
        return input_dt - td(minutes=input_dt.minute,
                             seconds=input_dt.second,
                             microseconds=input_dt.microsecond)


class Timespan_Day(TimespanUnit):
    """A timespan represented in days"""

    @classmethod
    def add_time(cls, input_date, amount):
        super().add_time(input_date, amount)
        return input_date + rd.relativedelta(days=+amount)

    @classmethod
    def round_time_backwards(cls, input_dt):
        """
        :param input_dt: the time to round backwards
        :return: datetime
        """
        super().round_time_backwards(input_dt)
        # round hours to the nearest day
        return input_dt - td(days=input_dt.hour,
                             minutes=input_dt.minute,
                             seconds=input_dt.second,
                             microseconds=input_dt.microsecond)


class Timespan_Week(TimespanUnit):
    """A timespan represented in weeks"""

    @classmethod
    def add_time(cls, input_date, amount):
        super().add_time(input_date, amount)
        return input_date + rd.relativedelta(weeks=amount)

    @classmethod
    def round_time_backwards(cls, input_dt):
        """
        :param input_dt: the time to round backwards
        :return: datetime
        """
        super().round_time_backwards(input_dt)

        # round day of the week to the nearest monday
        return input_dt - td(days=input_dt.weekday(),
                             hours=input_dt.hour,
                             minutes=input_dt.minute,
                             seconds=input_dt.second,
                             microseconds=input_dt.microsecond)


class Timespan_Month(TimespanUnit):
    """A timespan represented in months"""

    @classmethod
    def add_time(cls, input_date, amount):
        super().add_time(input_date, amount)
        return input_date + rd.relativedelta(months=+amount)

    @classmethod
    def round_time_backwards(cls, input_dt):
        """
        :param input_dt: the time to round backwards
        :return: datetime
        """
        super().round_time_backwards(input_dt)

        # round to the start of the month
        return input_dt - td(days=input_dt.day-1,
                             hours=input_dt.hour,
                             minutes=input_dt.minute,
                             seconds=input_dt.second,
                             microseconds=input_dt.microsecond)


class Timespan_Year(TimespanUnit):
    """A timespan represented in years"""

    @classmethod
    def add_time(cls, input_date, amount):
        super().add_time(input_date, amount)
        return input_date + rd.relativedelta(years=+amount)

    @classmethod
    def round_time_backwards(cls, input_dt):
        """
        :param input_dt: the time to round backwards
        :return: datetime
        """
        super().round_time_backwards(input_dt)

        # round to the start of the year
        return dt(year=input_dt.year, month=1, day=1, hour=0, minute=0, second=0, microsecond=0)


class Timespan_Custom(Timespan):
    """A class representing an arbitrary span of time"""

    def __init__(self, start, end):
        super().__init__()
        self.start = start
        self.end = end
        self.length = self.length_timespan_seconds() #The length of a custom timespan is measured in seconds

    @classmethod
    def add_time(cls, input_date, amount):
        super().add_time(input_date, amount)
        return input_date + rd.relativedelta(seconds=+amount)


class DatetimeGenerator:

    def step(self, timespan, latest_dt):
        """Generate a list of datetime tuples """
        outList = []

        while timespan.start_dt <= latest_dt:
            outList.append((timespan.start_dt, timespan.end_dt))
            timespan.slide(timespan, timespan.length_km)

        return outList

    # Todo
    def slide(self, base_ts, slide_ts, amount):
        pass
