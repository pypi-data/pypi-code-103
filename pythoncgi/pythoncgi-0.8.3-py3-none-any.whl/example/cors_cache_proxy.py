#!/usr/bin/python3
from pythoncgi import (
    _SERVER, _HEADERS, _GET, _POST, _SESSION, _COOKIE,
    get_settings, update_settings,
    set_status, set_header, generate_range_headers,
    init, execute, main,
    print, print_flush, print_file, flush,
    log, log_construct,
    # should_return_304, should_read_from_cache_file, write_to_cache_file,
    basic_authorization, parse_authorization, set_authenticate_response,
)
from omnitools import crc32hd, dt2rfc822gmt, rfc822gmt2dt, str2html
import requests
import pickle
import time
import math
import os


# for apache:
# #
# # <FilesMatch \.py$>
# #    	SetEnv no-gzip 1
# #    	SetEnv dont-vary 1
# #	</FilesMatch>
# try GET http://127.0.0.1/cors_cache_proxy.py
# test case:
# download without session:                                                            error
# download (force reload) without session:                                             error
# enter session and download, proxy no cache,            client no if modified since:  fetch from origin (notice response lag)
# enter session and download, proxy no cache,            client has if modified since: fetch from origin (notice response lag)
# enter session and download, proxy has unexpired cache, client no if modified since:  return cached response
# enter session and download, proxy has unexpired cache, client has if modified since: return 304
# enter session and download, proxy has expired cache,   client no if modified since:  fetch from origin (notice response lag)
# enter session and download, proxy has expired cache,   client has if modified since: fetch from origin (notice response lag)
# enter session and download (force reload), proxy no/has expired cache, client no/has if modified since: fetch from origin (notice response lag)


init()


def validate_request():
    if "session" not in _COOKIE:
        return False
    if "download" not in _POST:
        return False
    return True


def get_cache_fp():
    return os.path.join("_cache", crc32hd(_POST["download"])+".cache")


def read_cache_fp():
    return pickle.loads(open(get_cache_fp(), "rb").read())


# compare
# client if modified since value
# >=
# cache last modified value
# or compare
# rfc822gmt2dt(cache["headers"]["Expires"]).timestamp()
# >=
# time.time()
def should_return_304():
    if not validate_request():
        return False
    if "force_reload" in _GET:
        return False
    if os.path.isfile(get_cache_fp()):
        if "If-Modified-Since" in _HEADERS:
            ims = _HEADERS["If-Modified-Since"]
            ims = rfc822gmt2dt(ims)
            cache = read_cache_fp()
            if ims and "Last-Modified" in cache["headers"]:
                lastmodified = cache["headers"]["Last-Modified"]
                lastmodified = rfc822gmt2dt(lastmodified)
                if lastmodified and ims >= lastmodified:
                    for k, v in cache["headers"].items():
                        set_header(k, v)
                    return True
            # to do: expires header
            # to do: Etag header
    return False


# compare
# cache modified time + origin cache control (i.e. X-Cache-Control) max-age
# >=
# time.time()
# or compare
# rfc822gmt2dt(cache["headers"]["Expires"]).timestamp()
# >=
# time.time()
def should_read_from_cache_file():
    if not validate_request():
        return False
    if "force_reload" in _GET:
        return False
    if os.path.isfile(get_cache_fp()):
        cache = read_cache_fp()
        expire_dt = None
        now = time.time()
        if "X-Cache-Control" in cache["headers"]:
            if "max-age=" in cache["headers"]["X-Cache-Control"]:
                max_age = int(cache["headers"]["X-Cache-Control"].split("max-age=")[1].split(",")[0])
                lastmodified = math.floor(os.path.getmtime(get_cache_fp()))
                expire_dt = lastmodified+max_age
        # to do: expires header
        if expire_dt:
            if expire_dt >= now:
                set_status(cache["status_code"])
                for k, v in cache["headers"].items():
                    set_header(k, v)
                print(cache["cache"], end="")
                return True
        # to do: Etag header
    return False


def write_to_cache_file(cache):
    fp = get_cache_fp()
    try:
        os.makedirs(os.path.dirname(fp))
    except:
        pass
    try:
        open(fp, "wb").write(pickle.dumps(cache))
    except:
        pass


@execute(
    "get",
    authentication=lambda: True
)
def get():
    _download = '''<div><form method="post"><input type="hidden" name="download" value="https://i.imgur.com/OSf1vAx.jpeg"/>{}<input class="download" type="submit" value="Download{}"/></form></div>'''
    download = _download.format("", "")+_download.format('<input type="hidden" name="force_reload" value=""/>', " (force reload)")
    print('''
<html>
<head>
<title>test</title>
</head>
<body>
<h3>Session: "{}"</h3>
<div><input class="session" type="button" value="Click to enter a session name"/></div>
<div><input class="remove" type="button" value="Click to remove session"/></div>

<h3>Download</h3>
{}
<script>
var session = document.querySelector(".session");
var remove = document.querySelector(".remove");
if (session) {{
    session.addEventListener("click", function(){{
        document.cookie = "session="+prompt("Enter a session name:");
        window.location.reload(true);
    }});
}}
if (remove) {{
    remove.addEventListener("click", function(){{
        document.cookie = "session=;expires=Thu, 01 Jan 1970 00:00:00 GMT";
        window.location.reload(true);
    }});
}}
</script>
</body>
</html>
'''.format(
        "" if "session" not in _COOKIE else str2html(_COOKIE["session"]),
        download,
    ))


@execute(
    method="post",
    cacheable=True,
    cache_norm=should_return_304,
    cache_strat=should_read_from_cache_file,
    cache_store=write_to_cache_file,
    authentication=lambda: True
)
def post():
    set_header("Access-Control-Allow-Credentials", "true")
    set_header("Access-Control-Allow-Origin", "/".join(_HEADERS["HTTP_REFERER"].split("/")[:3]))
    set_header("Access-Control-Allow-Methods", "POST")
    set_header("Access-Control-Allow-Headers", "*")
    if validate_request():
        r = requests.get(_POST["download"])
        for k in ["Content-Type", "Last-Modified", "Expires"]:
            if k in r.headers:
                set_header(k, r.headers[k])
        if "Cache-Control" in r.headers:
            set_header("X-Cache-Control", r.headers["Cache-Control"])
        set_header("Cache-Control", "max-age=0, must-revalidate")
        print(r.content, end="")
    else:
        set_status(500)
        print("no session specified<br>please go back")


if __name__ == "__main__":
    main()

