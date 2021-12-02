from datetime import datetime

import puremagic
import pydicom
from nasminer import sql
from sqlalchemy import Table
from sqlalchemy.dialects.postgresql import insert as pinsert

tablename = 'dicom'
dicomt = Table(tablename, sql.meta, autoload=True, autoload_with=sql.db)


def can_handle(filepath):
    try:
        ext = puremagic.from_file(filepath)
    except:
        return False
    return ext == '.dcm'


def process_file(filepath, conn, fileid):
    ds = pydicom.filereader.dcmread(filepath)

    modality = ds[0x08, 0x60].value
    device = ds[0x08, 0x1090].value
    pid = ds[0x10, 0x20].value
    psex = ds[0x10, 0x40].value

    pname = ds[0x10, 0x10].value
    if isinstance(pname, str):
        fname = pname
        gname = None
    else:
        fname = pname.family_name
        gname = pname.given_name

    sdate = ds[0x08, 0x20].value
    stime = ds[0x08, 0x30].value
    dtraw = sdate + stime
    dt = datetime.strptime(dtraw, '%Y%m%d%H%M%S')

    pbirthraw = ds[0x10, 0x30].value
    try:
        pbirth = datetime.strptime(pbirthraw, '%Y%m%d').date()
    except ValueError:
        pbirth = None

    dbvalues = dict(
        dt=dt,
        modality=modality,
        device=device,
        patient_name=fname,
        patient_fname=gname,
        patient_id=pid,
        patient_birth=pbirth,
        patient_sex=psex,
    )
    i = pinsert(dicomt).values(**dbvalues, fileid=fileid)
    i = i.on_conflict_do_update(constraint='dicom_fileid_unique', set_=dbvalues)
    conn.execute(i)

    return True
