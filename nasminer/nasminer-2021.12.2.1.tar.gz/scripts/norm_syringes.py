import io
import os
import sys
import traceback
from collections import defaultdict
from functools import partial
from os import path, walk
from zipfile import ZipFile

import numpy as np
import pandas as pd
from nasminer.syringes.match_syr_lbl import detect_known_label

pdtonum = partial(pd.to_numeric, errors='coerce')
readcsv = partial(pd.read_csv, sep=',', index_col=False)
dtformat = '%Y-%m-%d %H:%M:%S.%f'


def test_file(filepath):
    headers1 = b'datetime,syringe,volume'
    headers2 = b'timens,syringe,volume'
    headers3 = b'timestamp,syringe,volume'
    headers4 = b'timestampns,syringe,volume'
    with open(filepath, 'rb') as f:
        line = f.readline().rstrip()
    if path.basename(filepath) == 'seringues.txt':
        return 'evenio'
    elif line == headers1:
        return 'datetime'
    elif line == headers2:
        return 'timens'
    elif line == headers3:
        return 'timestamp'
    elif line == headers4:
        return 'timestampns'
    else:
        return None


def transform_index(dttype, idx):
    if dttype == 'datetime':
        idx = pd.to_datetime(idx, format=dtformat)
    elif dttype in ['timens', 'timestamp', 'timestampns']:
        idx = pdtonum(idx)
        idx = pd.to_datetime(idx, unit='ns')
    else:
        idx = None
    return idx


def populate_dict(topdir):
    syrfolders = defaultdict(list)
    for root, _, files in walk(topdir):
        for filename in files:
            _, ext = path.splitext(filename)
            if ext.lower() not in ['.csv', '.txt']:
                continue
            filepath = path.join(root, filename)
            filetype = test_file(filepath)
            if filetype:
                print(f'Found {filename} of type {filetype} in {root}')
                syrfolders[root].append((filetype, filename))
    return syrfolders


def process_syre_file(filepath, dtfield):
    df = readcsv(filepath)
    idx = transform_index(dtfield, df[dtfield])
    df['timestamp'] = idx
    df = df.pivot_table(index='timestamp', columns='syringe', values='volume')
    return df


def process_evenio_file(filepath):
    with open(filepath, 'rb') as ftmp:
        line1 = ftmp.readline()
        ftmp.seek(0)
        fd = io.BytesIO()
        if not line1.startswith(b'temps,'):
            # One version of Evenio forgets the time header. Prepend it.
            fd.write(b'temps,')
        fd.write(ftmp.read())
    fd.seek(0)
    df = readcsv(fd, encoding='latin1')
    idx = transform_index('datetime', df['temps'])
    df['timestamp'] = idx
    df = df.set_index('timestamp')
    df = df.apply(pdtonum)
    return df


def merge_files(root, files):
    dfs = []
    for filetype, filename in files:
        filepath = path.join(root, filename)
        if filetype == 'evenio':
            dftmp = process_evenio_file(filepath)
        else:
            dftmp = process_syre_file(filepath, filetype)
        dfs.append(dftmp)
    df = pd.concat(dfs, axis=0)
    df = df.dropna(axis='columns', how='all')
    df = df.dropna(axis='rows', how='all')
    df = df.sort_index()
    df['timens'] = df.index.astype(np.int64)
    return df


def transform_files(indict):
    for root, files in indict.items():
        print(f'Merging {root}')
        os.chdir(root)
        try:
            df = merge_files(root, files)
        except Exception:
            traceback.print_exc()
            continue
        df = df.rename(detect_known_label, axis=1)
        print(df.head())
        df.to_csv('seringues_norm.csv', index_label='datetime', date_format=dtformat)


def ziparchive_old(indict):
    for root, files in indict.items():
        print(f'Archiving {root}')
        os.chdir(root)
        with ZipFile('seringues_old.zip', 'w') as myzip:
            for _, f in files:
                myzip.write(f)


def rm_old(indict):
    for root, files in indict.items():
        print(f'Cleaning {root}')
        os.chdir(root)
        for _, f in files:
            os.remove(f)


if __name__ == '__main__':
    topdir = sys.argv[1]
    d = populate_dict(topdir)
    transform_files(d)
    ziparchive_old(d)
    rm_old(d)
