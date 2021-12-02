import traceback
from datetime import datetime
from operator import methodcaller
from os import path, walk

import pandas as pd
from sqlalchemy import Table
from sqlalchemy.dialects.postgresql import insert as pinsert

from nasminer import common, dicom, edf, ixtrend, mict, sql, syringes

available_modules = [syringes, edf, ixtrend, mict, dicom]

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


def run(topdir):
    with sql.db.connect() as conn:
        existing = read_existing(conn)

        for root, _, files in walk(topdir, followlinks=True):
            folder = path.relpath(root, topdir)
            for filename in files:
                filepath = path.join(root, filename)

                mtimeseconds = path.getmtime(filepath)
                mtime = datetime.fromtimestamp(mtimeseconds)

                try:
                    existing_mtime = existing.loc[folder, filename]['mtime']
                    if mtime <= existing_mtime:
                        # print(f'existing: {filepath}')
                        continue
                except KeyError:
                    pass

                fsize = path.getsize(filepath)
                md5hash = common.calcmd5(filepath)

                # Find a module in available_modules which can handle the file
                mod_can_handle = methodcaller('can_handle', filepath)
                matchingmods = filter(mod_can_handle, available_modules)
                matchingmod = next(matchingmods, None)
                filetype = (
                    matchingmod.__name__.split('.')[-1] if matchingmod else 'unknown'
                )
                location = common.getLocation(filepath)

                print(f'{filetype}: {filepath}')

                i = pinsert(filest).returning(filest.c.id)
                i = i.values(
                    folder=folder,
                    filename=filename,
                    size=fsize,
                    mtime=mtime,
                    md5=md5hash,
                    filetype=filetype,
                    location=location,
                )
                i = i.on_conflict_do_update(
                    constraint='filepath_unique',
                    set_=dict(size=fsize, mtime=mtime, md5=md5hash, filetype=filetype),
                )

                res = conn.execute(i)
                fileid = res.fetchone()['id']

                if matchingmod is None:
                    continue

                try:
                    res = matchingmod.process_file(filepath, conn, fileid)
                except Exception:
                    traceback.print_exc()
                    continue
