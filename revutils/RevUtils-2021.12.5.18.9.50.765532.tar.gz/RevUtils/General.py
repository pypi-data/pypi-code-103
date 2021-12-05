import time
from datetime import datetime as dt
import gzip
import os
from datetime import datetime, timedelta
from random import randint
from pathlib import Path
from . import OS


def now_dt_str():
    return dt.now().strftime('%Y-%m-%d.%H-%M-%S')


def decompress_gzip(data):
    return gzip.decompress(data)


def compress_gzip(data):
    return gzip.compress(data)


def compress_str_gzip(text: str):
    return compress_gzip(text.encode())


def make_dirs_if_not_exists(path):
    if not os.path.exists(path):
        os.makedirs(path)


def file_exists(path: str):
    return os.path.isfile(path)


def dir_exists(path: str):
    return os.path.isdir(path)


def dt_now():
    return datetime.now()


def time_delta_seconds(d1: datetime, d2: datetime):
    return (d1 - d2).total_seconds()


def sec_until_time(_t: time):
    start = datetime.combine(datetime.today(), _t)
    sec_until_datetime(start)


def sec_until_datetime(_dt: datetime):
    next_run = time_delta_seconds(_dt, dt_now())
    if next_run <= 0:
        _dt += timedelta(days=1)
        next_run = time_delta_seconds(_dt, dt_now())
    return next_run


def sec_until_midnight():
    midnight = datetime.today() + timedelta(days=1)
    midnight = (midnight - dt_now()).total_seconds()
    return midnight


def sleep_rand_time(a, b):
    time.sleep(randint(a, b))


def is_hour_between(h1, h2):
    _now = dt_now()
    if _now.hour >= h1 or _now.hour <= h2:
        return True
    return False


def file_modification_time(path):
    try:
        mtime = os.path.getmtime(path)
        mtime = dt.fromtimestamp(mtime)
    except:
        return dt(1, 1, 1)
    return mtime


def file_path(_file_):
    return os.path.dirname(_file_)


def recursive_list_path(path, dirs=False, files=True):
    items = []

    for p in Path(path).rglob('*'):
        if (not files and p.is_file()) or (not dirs and p.is_dir()):
            continue

        items.append(p.as_posix())

    return items


def read_file_degzip_utf8(file) -> str:
    file = Path(file)
    file = file.read_bytes()
    file = decompress_gzip(file).decode('utf8')
    return file


def gen_os_exe_name(file: str):
    if OS.is_windows():
        if not file.endswith('.exe'):
            file = f'{file}.exe'
    else:
        if file.endswith('.exe'):
            file.removesuffix('.exe')
    return file
