#!/usr/bin/python3
from pythoncgi import (
    _SERVER, _HEADERS, _GET, _POST, _SESSION, _COOKIE,
    get_settings, update_settings,
    set_status, set_header, generate_range_headers,
    init, execute, main,
    print, print_flush, print_file, flush,
    log, log_construct,
    should_return_304, should_read_from_cache_file, write_to_cache_file,
    basic_authorization, parse_authorization, set_authenticate_response,
)
import os
import re
import math


# try GET http://127.0.0.1/zippyshare_remote_upload.py?p=1&f=/bigfile.bin
init()
HARD_LIMIT = 500*1024*1024
DOCUMENT_ROOT = os.path.normpath(os.path.join(_SERVER["DOCUMENT_ROOT"], ".."))


def get_fp(what):
    what = what.split("/")
    if not what[0]:
        what = what[1:]
    if not what[-1]:
        what = what[:-1]
    what = os.path.join(DOCUMENT_ROOT, *what)
    if re.search(r"((\\|/)\.\.|\.\.(\\|/))", what) or what.startswith(".."):
        raise NameError(what.replace(DOCUMENT_ROOT, ""), "has '..'")
    elif not os.path.exists(what):
        raise FileNotFoundError(what.replace(DOCUMENT_ROOT, ""))
    elif not os.path.isfile(what):
        raise IsADirectoryError(what.replace(DOCUMENT_ROOT, ""))
    return what


def get_current_range(size, parts, part):
    range = [HARD_LIMIT * (part - 1), HARD_LIMIT * part - 1]
    if part == parts:
        range[1] = size-1
    set_header("X-PS", str(parts))
    set_header("Content-Range", "bytes={}-{}/{}".format(*range, size))
    set_header("Content-Length", str(range[1]-range[0]+1))
    return range


def get_file():
    if "p" not in _GET:
        raise IndexError
    part = _GET["p"]
    if not part.isdigit():
        raise ValueError(part)
    part = int(part)
    if part < 1:
        raise ValueError(part)
    f = get_fp(_GET["f"])
    size = os.path.getsize(f)
    parts = math.ceil(size/HARD_LIMIT)
    if part > parts:
        raise ValueError(part)
    fo, _ = generate_range_headers(
        fp=f,
        disposition="attachment"
    )
    range = get_current_range(size, parts, part)
    return fo, range


@execute(
    method="get",
    authentication=lambda: True,
)
def get():
    if "f" in _GET:
        fo, range = get_file()
        if range:
            print_file(fo=fo, range=range)
    else:
        set_status(404)


@execute(
    method="head",
    authentication=lambda: True,
)
def head():
    if "f" in _GET:
        get_file()
    else:
        set_status(404)


if __name__ == '__main__':
    main()

