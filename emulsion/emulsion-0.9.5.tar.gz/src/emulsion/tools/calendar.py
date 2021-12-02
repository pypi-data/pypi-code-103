"""@package emulsion.tools.calendar

A Python implementation of the EMuLSion framework.

(Epidemiologic MUlti-Level SImulatiONs).

Classes and functions for the definition of EMuLSion calendars.

"""


from   sortedcontainers      import SortedDict


#  ______                    _   _
# |  ____|                  | | (_)
# | |__  __  _____ ___ _ __ | |_ _  ___  _ __  ___
# |  __| \ \/ / __/ _ \ '_ \| __| |/ _ \| '_ \/ __|
# | |____ >  < (_|  __/ |_) | |_| | (_) | | | \__ \
# |______/_/\_\___\___| .__/ \__|_|\___/|_| |_|___/
#                     | |
#                     |_|

class InvalidIntervalException(Exception):
    """Exception raised when trying to insert an inconsistent event in
    the calendar.

    """
    def __init__(self, begin, end):
        super().__init__()
        self.value = (begin, end)

    def __str__(self):
        return 'Invalid dates interval {}'.format(self.value)


#  ______                _   _
# |  ____|              | | (_)
# | |__ _   _ _ __   ___| |_ _  ___  _ __  ___
# |  __| | | | '_ \ / __| __| |/ _ \| '_ \/ __|
# | |  | |_| | | | | (__| |_| | (_) | | | \__ \
# |_|   \__,_|_| |_|\___|\__|_|\___/|_| |_|___/




def date_in(begin, end, period=None):
    """Return a function which tests if a date belongs to the
    specified interval. If a period is specified, the test relies upon
    the periodicity, otherwise dates are considered absolute.

    """
    if period is not None:
        begin, end = begin % period, end % period
        if begin <= end:
            def test_date(date):
                """Check that the specified date belongs to the event interval,
                considering the periodicity.

                """
                return begin <= (date % period) <= end
        else:
            def test_date(date):
                """Check that the specified date belongs to the event interval,
                considering the periodicity and the fact that the end
                date appears before the begin date in a civil year.

                """
                return (date % period) <= begin or (date % period) >= end
    else:
        if begin <= end:
            def test_date(date):
                """Check that the specified date belongs to the event interval,
                considered as absolute (no periodicity).

                """
                return begin <= date <= end
        else:
            raise InvalidIntervalException(begin, end)
    return test_date





#  ______               _    _____      _                _
# |  ____|             | |  / ____|    | |              | |
# | |____   _____ _ __ | |_| |     __ _| | ___ _ __   __| | __ _ _ __
# |  __\ \ / / _ \ '_ \| __| |    / _` | |/ _ \ '_ \ / _` |/ _` | '__|
# | |___\ V /  __/ | | | |_| |___| (_| | |  __/ | | | (_| | (_| | |
# |______\_/ \___|_| |_|\__|\_____\__,_|_|\___|_| |_|\__,_|\__,_|_|


class EventCalendar:
    """The EventCalendar class is intended to handle events and
    periods of time. Dates/times are given to the calendar in a
    human-readable format, and converted to integers (simulation
    steps).

    """
    def __init__(self, calendar_name, step_duration, origin,
                 period=None, **initial_dates):
        """Initialize the calendar using the specified information.

        Args:
        - calendar_name: name of the calendar
        - step_duration: actual duration of one simulation step
          (timedelta)
        - origin: date/time value of the beginning of the calendar
          (datetime)
        - period: if the calendar is periodic, actual duration of the
          period (timedelta), None otherwise
        - initial_dates: initial dictionary of events (event name as
          key, dict as value with either begin/end dates or one
          date)

        """
        self.calendar_name = calendar_name
        self.step = 0
        self.step_duration = step_duration
        self.origin = origin
        self.current_date = self.origin
        self.events = SortedDict()
        self.description = SortedDict()
        self.period = None if period is None\
          else period // self.step_duration
        for name, value in initial_dates.items():
            self.add_event(name, value)


    def increment(self, steps=1):
        """Advance the current date by the specified number of
        simulation steps.

        """
        self.current_date += self.step_duration * steps

    def step_to_date(self, step):
        """Return the date when the specified step begins."""
        return self.origin + self.step_duration * step

    def date_to_step(self, date):
        """Return the step including the specified date."""
        return (date - self.origin) // self.step_duration


    def add_event(self, name, value):
        """Add the specified event to the calendar. An event is
        characterized by its name and a tuple indicating the begin and
        end dates.

        """
        begin_date, end_date = value
        begin = self.date_to_step(begin_date)
        end = self.date_to_step(end_date)
        if end < begin and self.period is None:
            raise InvalidIntervalException(begin, end)
        self.description[name] = value
        self.events[name] = date_in(begin, end, self.period)

    def get_events(self):
        """Return the list of events contained in the current calendar."""
        return list(self.description.keys())

    def __getitem__(self, name):
        return self.events[name]
