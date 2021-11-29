"""Interpolate weather."""

from building_plus.basic.two_way_interp import two_way_interp

import datetime as dt

def interpolate_weather(weather, d):
    test_weather = {}
    date = []
    test_weather['timestamp'] = date
    for x in range(len(d)):
        if d[x]<weather['timestamp'][0] and d[x].year == weather['timestamp'][0].year:
            date.append(weather['timestamp'][0])
        elif d[x]>weather['timestamp'][-1] and d[x].year == weather['timestamp'][-1].year:
            date.append(weather['timestamp'][-1])
        elif d[x]<weather['timestamp'][0] or d[x]<weather['timestamp'][-1]:
            date.append(dt.datetime(weather['timestamp'][0].year,d[x].month,d[x].day,d[x].hour,d[x].minute,d[x].second))
        else:
            date.append(d[x])
    d0 = weather['timestamp'][0].timestamp()
    def to_timestamp(d,d0):
        return [d[x].timestamp()-d0 for x in range(len(d))]
    for x in weather:
        if x!='timestamp' and x!= 'designation':
            test_weather[x]= two_way_interp(to_timestamp(date,d0),to_timestamp(weather['timestamp'],d0),weather[x])
    return test_weather
