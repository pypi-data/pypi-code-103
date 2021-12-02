import math

import numpy as np
from scipy import stats


def stable_against_known(x,
                         y,
                         known: float,
                         upper_limit: float,
                         lower_limit: float,
                         std_max: float = 0.05,
                         sem_max: float = 0.05,
                         r_min: float = None,
                         slope_upper_limit: float = None,
                         slope_lower_limit: float = None,
                         ) -> bool:
    """
    Custom method for determining if data is stable compared to some known value. Based on if it falls within some
    limits. For the data, it must have a standard deviation less than std_max, and both its mean and mode need to lie
    between the known - lower_limit and known + upper_limit values, and an sem less than sem_max, and the range of
    the data is less than the sum of the upper and lower limits multiplied by some limit constant. And if the
    r value from doing a linear regression is less than r_min and the slope from doing a linear regression is
    plus/minus slope upper and lower limits.

     :param x: 1d array of the x part of some data
    :param y: 1d array of the y part of some data
    :param float, known: a known reference value to compare the data to
    :param float, upper_limit: how much above the known value the mean and mode of the data can be to be determined
        stable
    :param float, lower_limit: how much below the known value the mean and mode of the data can be to be determined
        stable
    :param float, std_max: maximum standard deviation the data can have to be determined as stable
    :param float, sem_max: maximum standard error the data can have to be determined as stable
    :param float, r_min: minimum r when doing a linear regression on the data required for the data =to be
        determined as stable
    :param float, slope_upper_limit: how much above zero the slope from doing a linear regression can be in order for
        the data to be determined as stable
     :param float, slope_lower_limit: how much below zero the slope from doing a linear regression can be in order for
        the data to be determined as stable
    :return:
    """
    if r_min is None:
        r_min = 0
    if slope_upper_limit is None:
        slope_upper_limit: float = 999
    if slope_lower_limit is None:
        slope_lower_limit: float = 999
    n = len(x)
    limit_const = 1.5
    limit_range = (upper_limit + lower_limit) * limit_const
    data_median = np.median(y)
    data_mode = stats.mode(y)
    data_mode = data_mode.mode[0]
    data_std = np.std(y)
    data_sem = data_std/(math.sqrt(n))
    low = known - lower_limit
    high = known + upper_limit
    range = max(y) - min(y)
    slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)

    median_good = low <= data_median <= high
    mode_good = low <= data_mode <= high
    std_good = data_std <= std_max
    sem_good = data_sem <= sem_max
    range_good = range <= limit_range
    r_good = r_min < r_value
    slope_good = (-1 * slope_lower_limit) <= slope <= slope_upper_limit

    if median_good and mode_good and std_good and sem_good and range_good and r_good and slope_good:
        return True
    else:
        return False