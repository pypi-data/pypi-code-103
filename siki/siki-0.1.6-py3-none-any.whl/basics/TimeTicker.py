# -*- coding: utf-8 -*-
# Author: Orlando Chen
# Created: May 09, 2018
# Modified: Jan 22, 2021

MS_PER_SECOND = 1000
MS_PER_MINUTE = 60000
MS_PER_HOUR = 3600000
MS_PER_DAY = 86400000


def time_with_msg(message=None) -> str:
    """
    return to caller a string message with timestamp for debug purpose

    @Args:
    * [strMessage] message to display, if none, the returning will just 
        only a timestamp of the format YYYY-mm-dd HH:MM:SS.ms

    @Returns:
    * [str] returning a string with timestamp
    """
    import datetime
    if message is None:
        return time_with_fmt("%Y-%m-%d %H:%M:%S.%f")
    else:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
        return f"{timestamp} {message}"


def time_with_fmt(fmt="%Y-%m-%d %H:%M:%S") -> str:
    """
    Returning a formatted string of time

    @Args:
    * [format] str, something like %Y-%m-%d %H:%M:%S.%f

    @Returns:
    * [str] the formatted string of time
    """
    import datetime
    return datetime.datetime.now().strftime(fmt)


def time_since1970() -> float:
    """
    Returning a decimal number with couting the last seconds since 1970

    @Returns:
    * [float] 
    """
    import time
    return time.time()
