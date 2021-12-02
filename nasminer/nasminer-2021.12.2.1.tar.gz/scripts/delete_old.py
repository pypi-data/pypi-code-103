import sys
from os import path, walk

import pandas as pd
from nasminer import common, sql
from sqlalchemy import Table
from sqlalchemy.sql import and_

MAXDELETE = int(common.config.get('db', 'deletemaxrows', fallback='100'))


tablename = 'files'
filest = Table(tablename, sql.meta, autoload=True, autoload_with=sql.db)


def read_existing(conn):
    df = pd.read_sql_table(
        tablename,
        conn,
        columns=['mtime'],
        index_col=['folder', 'filename'],
        parse_dates=['mtime'],
    )
    return df


def get_missing(topdir):
    with sql.db.connect() as conn:
        indb = read_existing(conn)
    print(f'Entries in DB: {len(indb)}')

    ondisk = []
    for root, _, files in walk(topdir, followlinks=True):
        folder = path.relpath(root, topdir)
        for filename in files:
            ondisk.append((folder, filename))

    print(f'Files on disk: {len(ondisk)}')
    idxondisk = pd.Index(ondisk, name=('folder', 'filename'))
    missing = indb.index.difference(idxondisk)
    return missing


def run(topdir):
    missing = get_missing(topdir)
    if len(missing) > MAXDELETE:
        print(f'Error: too much missing ({len(missing)}) entries')
        return
    print(f'Deleting DB records for {len(missing)} missing files')
    with sql.db.connect() as conn:
        for folder, filename in missing:
            d = filest.delete().where(
                and_(filest.c.folder == folder, filest.c.filename == filename)
            )
            conn.execute(d)


if __name__ == '__main__':
    topdir = sys.argv[1]
    run(topdir)
