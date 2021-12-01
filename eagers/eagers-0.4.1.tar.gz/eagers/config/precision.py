"""Defines variables relating to chosen precision values.
"""


# Datetime rounding precision.
# Example: If precision is 'second':
#   1. 1/2 sec will be added.
#   2. However many many milliseconds (the next highest precision level)
#       the datetime now has will be subtracted from it.  I.e. the
#       datetime will be "floored" in terms of milliseconds.

# Precision used in rounding datetimes.
DATETIME_ROUNDING_PRECISION = 'second'

# timedelta field to be used in "flooring" to a rounded datetime.
DATETIME_ROUNDING_TIMEDELTA_FIELD = 'microsecond'
