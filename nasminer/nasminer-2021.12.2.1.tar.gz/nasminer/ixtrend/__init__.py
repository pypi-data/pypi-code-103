import io
import os
from csv import DictReader

from nasminer import sql
from nasminer.csv import estimateDelimiters
from sqlalchemy import Table
from sqlalchemy.dialects.postgresql import insert as pinsert

from .analyze_csv import getDateTime, getFileType

tablename = 'ixtrend'
ixtrendt = Table(tablename, sql.meta, autoload=True, autoload_with=sql.db)


def can_handle(filepath):
    try:
        getFileType(filepath)
    except ValueError:
        return False
    else:
        return True


def analyze_file(filepath, sep, dec):
    # Do some juggling between opening the file in byte / text mode
    # fd.seek(n, os.SEEK_END) needs binary. DictReader needs text.
    with open(filepath, 'rb') as binfd:
        txtfd = io.TextIOWrapper(binfd, encoding='latin1', errors='replace')
        headerline = txtfd.readline()
        txtfd.seek(0)

        # Read first line
        reader = DictReader(txtfd, delimiter=sep)
        sample = next(reader)
        dtlbl, dtbegin = getDateTime(sample, dec)
        del sample[dtlbl]
        try:
            del sample[None]
        except KeyError:
            pass
        colnames = list(sample.keys())

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
        _, dtend = getDateTime(sample, dec)
    return (colnames, dtlbl, dtbegin, dtend)


def process_file(filepath, conn, fileid):
    idname, idtype = getFileType(filepath)
    sep, dec = estimateDelimiters(filepath)
    colnames, dtlbl, dtbegin, dtend = analyze_file(filepath, sep, dec)
    dbvalues = dict(
        dtbegin=dtbegin,
        dtend=dtend,
        datetime_label=dtlbl,
        signals=colnames,
        seperator=sep,
        decimal=dec,
        signal_type=idtype,
        patientinfo=idname,
    )
    i = pinsert(ixtrendt).values(**dbvalues, fileid=fileid)
    i = i.on_conflict_do_update(constraint='ixtrend_fileid_unique', set_=dbvalues)
    conn.execute(i)
    return True
