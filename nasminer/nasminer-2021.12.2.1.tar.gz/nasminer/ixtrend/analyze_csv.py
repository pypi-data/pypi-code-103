from csv import DictReader
from datetime import datetime
from os import path
from re import match

import dateutil

defaultdt = datetime.now(tz=dateutil.tz.gettz('Europe/Paris'))


def getFileType(filepath):
    filename = path.basename(filepath)
    name, ext = path.splitext(filename)
    if ext != '.csv':
        raise ValueError('Unknown file type')
    pattern = r'(\(.+\))?([a-zA-Z_ ]+)\d*_(waves|numerics)'
    r = match(pattern, name)
    if r is None:
        raise ValueError('Unknown file type')
    idname = r.group(2).lower()
    idtype = r.group(3)
    return (idname, idtype)


def getDateTime(row, dec):
    dt = None
    try:
        lbl = 'Date Time'
        cellval = row[lbl]
        try:
            # dtformat = f'%Y-%m-%d %H:%M:%S{dec}%f'
            dt = dateutil.parser.parse(cellval, default=defaultdt)
            dt = dt.astimezone(dateutil.tz.UTC)
        except ValueError:
            dtformat = "%H:%M:%S"
            dt = datetime.strptime(cellval, dtformat)
        return (lbl, dt)
    except (KeyError, ValueError):
        pass
    try:
        lbl = 'Milliseconds since 01.01.1970'
        cellval = row[lbl]
        sec = float(cellval) / 1000
        dt = datetime.fromtimestamp(sec)
        return (lbl, dt)
    except (KeyError, ValueError):
        pass
    raise ValueError('Could not parse date/time')
