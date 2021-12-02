from datetime import datetime, timezone
from os import path
from pathlib import Path
from re import match

import pyedflib
from nasminer import sql
from sqlalchemy import Table
from sqlalchemy.dialects.postgresql import insert as pinsert

tablename = 'edf'
edft = Table(tablename, sql.meta, autoload=True, autoload_with=sql.db)


def can_handle(filepath):
    _, ext = path.splitext(filepath)
    return ext.lower() == '.edf'


def __match_serial(part):
    # pattern = r'root_2000036218_20210508_014255'
    pattern = r'root_(\d+)_\w+'
    m = match(pattern, part)
    if m:
        return m[1]
    else:
        return None


def getSerial(filepath):
    parts = Path(filepath).parent.parts
    for part in reversed(parts):
        res = __match_serial(part.lower())
        if res:
            break
    else:
        return None
    return res


def process_file(filepath, conn, fileid):
    edf = pyedflib.EdfReader(filepath)
    serial = getSerial(filepath)
    # Temporary test
    assert serial is None or len(serial) <= 10

    begin_ts = edf.getStartdatetime().timestamp()
    nsamplesPerChannel = edf.getNSamples()

    fs = 0
    channels = []
    end_ts = begin_ts
    for i in range(edf.signals_in_file):
        h = edf.getSignalHeader(i)
        channels.append(h['label'])
        fs = max(fs, h['sample_rate'])
        n = nsamplesPerChannel[i]
        end_ts_i = begin_ts + n / fs
        end_ts = max(end_ts, end_ts_i)
    edf.close()

    begin_dt = datetime.fromtimestamp(begin_ts, tz=timezone.utc)
    end_dt = datetime.fromtimestamp(end_ts, tz=timezone.utc)

    dbvalues = dict(
        dtbegin=begin_dt, dtend=end_dt, fs=fs, channels=channels, device=serial
    )
    i = pinsert(edft).values(**dbvalues, fileid=fileid)
    i = i.on_conflict_do_update(constraint='edf_fileid_unique', set_=dbvalues)
    conn.execute(i)

    return True
