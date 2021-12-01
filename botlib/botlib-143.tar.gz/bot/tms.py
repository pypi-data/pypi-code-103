# This file is placed in the Public Domain.


import datetime


def day():
    return str(datetime.datetime.today()).split()[0]


def elapsed(seconds, short=True):
    txt = ""
    nsec = float(seconds)
    year = 365 * 24 * 60 * 60
    week = 7 * 24 * 60 * 60
    nday = 24 * 60 * 60
    hour = 60 * 60
    minute = 60
    years = int(nsec / year)
    nsec -= years * year
    weeks = int(nsec / week)
    nsec -= weeks * week
    nrdays = int(nsec / nday)
    nsec -= nrdays * nday
    hours = int(nsec / hour)
    nsec -= hours * hour
    minutes = int(nsec / minute)
    sec = nsec - minutes * minute
    if years:
        txt += "%sy" % years
    if weeks:
        nrdays += weeks * 7
    if nrdays:
        txt += "%sd" % nrdays
    if years and short and txt:
        return txt
    if hours:
        txt += "%sh" % hours
    if nrdays and short and txt:
        return txt
    if minutes:
        txt += "%sm" % minutes
    if hours and short and txt:
        return txt
    if sec == 0:
        txt += "0s"
    else:
        txt += "%ss" % int(sec)
    txt = txt.strip()
    return txt


def parse_ymd(daystr):
    valstr = ""
    val = 0
    total = 0
    for c in daystr:
        if c in "1234567890":
            vv = int(valstr)
        else:
            vv = 0
        if c == "y":
            val = vv * 3600 * 24 * 365
        if c == "w":
            val = vv * 3600 * 24 * 7
        elif c == "d":
            val = vv * 3600 * 24
        elif c == "h":
            val = vv * 3600
        elif c == "m":
            val = vv * 60
        else:
            valstr += c
        total += val
    return total
