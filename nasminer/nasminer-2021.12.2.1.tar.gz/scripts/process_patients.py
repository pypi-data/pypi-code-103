import sys
from os import path

import pandas as pd
from sqlalchemy import Table
from sqlalchemy.exc import IntegrityError

from nasminer import sql

tablename = 'patients'
ixtrendt = Table(tablename, sql.meta, autoload=True, autoload_with=sql.db)

if __name__ == '__main__':
    infile = sys.argv[1]
    outfolder = path.dirname(infile)

    errfile = path.join(outfolder, 'patients_erreurs.xlsx')

    dfin = pd.read_excel(infile)
    dferr = dfin.iloc[0:0]

    with sql.db.connect() as conn:
        for _, row in dfin.iterrows():
            rowdata = row.to_dict()
            i = ixtrendt.insert(rowdata)
            try:
                conn.execute(i)
            except IntegrityError:
                dferr = dferr.append(row)

    # Dump errored lines
    dferr.to_excel(errfile, index=False)

    # Truncate input file
    dfblank = dfin.iloc[0:0]
    dfblank.to_excel(infile, index=False)
