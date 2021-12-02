import sys
from os import path

import pandas as pd
from nasminer import dicom, edf, ixtrend, mict, syringes
from sqlalchemy import Table, join, select

available_modules = [syringes, edf, ixtrend, dicom, mict]

from nasminer import common, sql

filest = Table('files', sql.meta, autoload=True, autoload_with=sql.db)
patientst = Table('patients', sql.meta, autoload=True, autoload_with=sql.db)


def dump_table(conn, tablename, outdir):
    modt = Table(tablename, sql.meta, autoload=True, autoload_with=sql.db)
    q = (
        select([modt, filest])
        .select_from(modt.join(filest, modt.c.fileid == filest.c.id))
        .order_by(filest.c.mtime)
    )
    df = pd.read_sql(q, conn)
    outfile = path.join(outdir, f'{tablename}.xlsx')
    print(f'Dumping table {tablename} to {outfile}')
    df.to_excel(outfile, index=False)


if __name__ == '__main__':
    outdir = sys.argv[1]

    tablenames = [m.tablename for m in available_modules]

    with sql.db.connect() as conn:
        patients = pd.read_sql(select([patientst]), conn)
        outfile = path.join(outdir, f'patients.xlsx')
        print(f'Dumping table patients to {outfile}')
        patients.to_excel(outfile, index=False)

        for t in tablenames:
            dump_table(conn, t, outdir)
