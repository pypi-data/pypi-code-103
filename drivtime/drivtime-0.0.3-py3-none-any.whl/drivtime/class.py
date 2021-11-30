from datetime import timedelta
from typing import List
import numpy as np 

def overview(daily: int, weekly: int, fortnightly: int) -> List:
    """[summary]

    Args:
        daily (int): Daily driving used
        weekly (int): Weekly driving used
        fortnightly (int): Fortnightly driving used time

    Returns:
        List: [description]
    """
    
    # Driving period limit
    daily_lim = timedelta(hours=9)
    weekly_lim = timedelta(hours=56)
    fortnightly_lim = timedelta(hours=90)

    # Exceptions
    weekly_exc = 2
    fortnightly_exc = 3

    # Fortnight matrix


def driving_check(history: List, current_week: int, current_day: int) -> str:
    """AI is creating summary for driving_check

    Args:
        history (List): [description]

    Returns:
        str: [description]
    """
    daily_lim = timedelta(hours=9)
    weekly_lim = timedelta(hours=56)
    fortnightly_lim = timedelta(hours=90)

    _week_idx = current_week - 1
    _day_idx = current_day - 1
    
    _exc_week_one = 0
    _exc_week_two = 0

    if(current_week==1):
        print(history[:current_day])
        _fortnight_value = timedelta(hours=sum(history[:current_day]))
        _week_value = timedelta(hours=sum(history[:current_day]))
        _exc_week_one = len(list(filter(lambda x: 9 <= x <= 10, history[:current_day])))
    elif(current_week==2):
        _fortnight_value = timedelta(hours=(sum(history[:7]) + sum(history[7:(7+current_day)])))
        _week_value = timedelta(hours=sum(history[7:(7+current_day)]))
        _exc_week_two = len(list(filter(lambda x: 9 <= x <= 10, history[7:(7+current_day)])))

    arr = [None]*14
    for idx, value in enumerate(history):
        arr[idx] = timedelta(hours=value)
    
    fortnight_mtx = np.reshape(arr, (2, 7))
    _day = daily_lim - fortnight_mtx[_week_idx][_day_idx]
    _week = weekly_lim - _week_value
    _fortnight = fortnightly_lim - _fortnight_value

    print(f'Driver with still has {_day} left today.')
    print(f'Driver with still has {_week} left for the current week.')
    print(f'Driver with still has {_fortnight} left for the fortnight.')

    print()


driving_check([1,2,3,4,1,7,7,7,7,9.5,10,10,4.5,2], 2, 7)