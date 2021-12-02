import io
import os
from csv import DictReader
from datetime import datetime
from functools import partial
from pathlib import Path
from re import match

import pandas as pd
from nasminer import sql
from nasminer.csv import estimateDelimiters
from sqlalchemy import Table
from sqlalchemy.dialects.postgresql import insert as pinsert

tablename = 'mict'
mictt = Table(tablename, sql.meta, autoload=True, autoload_with=sql.db)
pdtonum = partial(pd.to_numeric, errors='coerce')


def can_handle(filepath):
    return test_filename(filepath) and test_data(filepath)


def test_filename(filepath):
    fp = Path(filepath)
    if fp.suffix != '.csv':
        return False
    pattern = r'Trend_[0-9_-]+$'  # Trend_7-9-2021_9-3-52.csv
    r = match(pattern, fp.stem)
    return r is not None


def test_data(filepath):
    with open(filepath, 'r') as fd:
        line = fd.readline()
    return 'Time (GMT)' in line


def getDateTime(row):
    date = row['Date']
    time = row['Time (GMT)']
    dttxt = f'{date} {time}'
    dtformat = f'%m/%d/%Y %H:%M:%S'  # 05/26/2021 18:57:47
    return datetime.strptime(dttxt, dtformat)


def get_signals(filepath, sep: str, dec: str):
    df = pd.read_csv(filepath, sep=sep, decimal=dec)
    dfnum = df.apply(pdtonum, axis=1)
    dfnona = dfnum.dropna(axis=1, how='all')
    return set(dfnona.columns)


def analyze_file(filepath):
    # Do some juggling between opening the file in byte / text mode
    # fd.seek(n, os.SEEK_END) needs binary. DictReader needs text.
    sep, dec = estimateDelimiters(filepath)
    signals = get_signals(filepath, sep, dec)
    with open(filepath, 'rb') as binfd:
        txtfd = io.TextIOWrapper(binfd, encoding='latin1', errors='replace')
        headerline = txtfd.readline()
        txtfd.seek(0)

        # Read first line
        reader = DictReader(txtfd, delimiter=sep)
        sample = next(reader)
        dtbegin = getDateTime(sample)

        # Read last line
        max_line_length = 2 ** 10
        binfd.seek(-max_line_length, os.SEEK_END)
        lastline = binfd.readlines()[-1]
        buffer = io.StringIO(headerline)
        buffer.seek(0, os.SEEK_END)
        buffer.write(lastline.decode('latin1'))
        buffer.seek(0)
        reader = DictReader(buffer, delimiter=sep)
        sample = next(reader)
        dtend = getDateTime(sample)
    return (dtbegin, dtend, signals)


def process_file(filepath, conn, fileid):
    dtbegin, dtend, signals = analyze_file(filepath)
    dbvalues = dict(dtbegin=dtbegin, dtend=dtend, signals=signals)
    i = pinsert(mictt).values(**dbvalues, fileid=fileid)
    i = i.on_conflict_do_update(constraint='mict_fileid_unique', set_=dbvalues)
    conn.execute(i)
    return True
