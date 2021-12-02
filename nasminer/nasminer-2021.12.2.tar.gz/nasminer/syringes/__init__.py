from datetime import datetime
from functools import partial
from os import path

import pandas as pd
from nasminer import sql
from sqlalchemy import Table
from sqlalchemy.dialects.postgresql import insert as pinsert

readcsv = partial(pd.read_csv, sep=',', index_col=False, encoding='latin1')

tablename = 'syringes'
syringest = Table(tablename, sql.meta, autoload=True, autoload_with=sql.db)


def can_handle(filepath):
    return path.basename(filepath) == 'seringues_norm.csv'


def process_file(filepath, conn, fileid):
    df = readcsv(filepath)
    beginns = df['timens'].iloc[0]
    begin = datetime.fromtimestamp(beginns / 1e9)
    endns = df['timens'].iloc[-1]
    end = datetime.fromtimestamp(endns / 1e9)
    cols = df.columns
    cols = cols.drop(['datetime', 'timens']).values

    dbvalues = dict(dtbegin=begin, dtend=end, syringes=cols)
    i = pinsert(syringest).values(**dbvalues, fileid=fileid)
    i = i.on_conflict_do_update(constraint='syringes_fileid_unique', set_=dbvalues)
    conn.execute(i)

    return True
