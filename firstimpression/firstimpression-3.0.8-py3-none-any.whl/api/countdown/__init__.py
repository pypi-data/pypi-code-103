import datetime

from firstimpression.constants import APIS
from firstimpression.scala import ScalaPlayer


##################################################################################################
# CONSTANTS
##################################################################################################

NAME = APIS['countdown']

##################################################################################################
# Scala Player
##################################################################################################

scala = ScalaPlayer(NAME)

##################################################################################################
# MAIN FUNCTIONS API
##################################################################################################


def check_api():
    scala.debug('folder name: {}'.format(NAME))
    svars = scala.variables

    year = svars['end_year']
    month = svars['end_month']
    day = svars['end_day']
    hour = svars['end_hour']
    minute = svars['end_minute']
    second = svars['end_second']

    end_date = datetime.datetime(year, month, day, hour, minute, second)
    current_date = datetime.datetime.now()

    scala.debug('end_date: {} - current_date: {}'.format(end_date, current_date))

    if current_date > end_date:
        scala.warn('current_date is past the end date')
        svars['skipscript'] = True
    else:
        svars['skipscript'] = False
        time_delta = end_date - current_date

        scala.debug('time difference in timedelta: {}'.format(time_delta))

        days_remaining = time_delta.days
        years_remaining = days_remaining//365
        days_remaining -= years_remaining * 365
        weeks_remaining = days_remaining//7
        days_remaining -= weeks_remaining * 7

        seconds_remaining = time_delta.seconds
        hours_remaining = seconds_remaining//3600
        seconds_remaining -= hours_remaining * 3600
        minutes_remaining = seconds_remaining//60
        seconds_remaining -= minutes_remaining * 60

        scala.debug('years: {} - weeks: {} - days: {} - hours: {} - minutes: {} - seconds: {}'.format(years_remaining,
                                                                                                      weeks_remaining, days_remaining, hours_remaining, minutes_remaining, seconds_remaining))

        svars['remaining_year'] = years_remaining
        svars['remaining_week'] = weeks_remaining
        svars['remaining_day'] = days_remaining
        svars['remaining_hour'] = hours_remaining
        svars['remaining_minute'] = minutes_remaining
        svars['remaining_second'] = seconds_remaining


##################################################################################################
# MEDIA FUNCTIONS
##################################################################################################


##################################################################################################
# GET FUNCTIONS
##################################################################################################


##################################################################################################
# PARSE FUNCTIONS
##################################################################################################
