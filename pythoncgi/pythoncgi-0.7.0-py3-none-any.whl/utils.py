from omnitools import dt2rfc822gmt, rfc822gmt2dt, b64d_and_utf8d, str2html
import datetime
import json
import math
import os
import re


def obj_to_bytes(obj, html: bool = True):
    if isinstance(obj, str):
        obj = obj.encode()
    elif not isinstance(obj, bytes):
        try:
            obj = json.dumps(obj, indent=2)
            if html:
                obj = str2html(obj)
        except:
            obj = str(obj)
            if html:
                obj = str2html(obj)
        obj = obj.encode()
    return obj


def _cache_control(
        *,
        max_age: int = -1,
        s_max_age: int = -1,
        no_cache: bool = False,
        must_revalidate: bool = False,
        proxy_revalidate: bool = False,
        no_store: bool = False,
        private: bool = False,
        public: bool = False,
        must_understand: bool = False,
        no_transform: bool = False,
        immutable: bool = False,
        stale_while_revalidate: int = -1,
        stale_if_error: int = -1
):
    cc = ""
    def c():
        return ", " if cc else ""
    if max_age >= 0:
        cc += c()+"max_age={}".format(max_age)
    if s_max_age >= 0:
        cc += c()+"s_max_age={}".format(s_max_age)
    if no_cache:
        cc += c()+"no-cache"
    if must_revalidate:
        cc += c()+"must-revalidate"
    if proxy_revalidate:
        cc += c()+"proxy-revalidate"
    if no_store:
        cc += c()+"no-store"
    if private:
        cc += c()+"private"
    if public:
        cc += c()+"public"
    if must_understand:
        cc += c()+"must-understand"
    if no_transform:
        cc += c()+"no-transform"
    if immutable:
        cc += c()+"immutable"
    if stale_while_revalidate != -1:
        cc += c()+"stale-while-revalidate"
    if stale_if_error != -1:
        cc += c()+"stale-if-error"
    if cc:
        from .core import set_header
        set_header("Cache-Control", cc)


def _should_return_304(headers, fp: str = None):
    from .core import set_header
    if not fp or not os.path.isfile(fp):
        return False
    lastmodified = math.floor(os.path.getmtime(fp))
    lastmodified = datetime.datetime.fromtimestamp(lastmodified)
    set_header("Last-Modified", dt2rfc822gmt(lastmodified))
    if "If-Modified-Since" in headers:
        ims = rfc822gmt2dt(headers["If-Modified-Since"])
        if ims and ims >= lastmodified:
            return True
    return False


def parse_range(headers):
    m = re.search(r"bytes=(\d+)-(\d+)?$", headers["Range"])
    if m:
        start, end = [int(x) if x else x for x in m.groups()]
        if end and end < start:
            from .core import set_status
            set_status(416)
            raise ValueError("end [{}] < start [{}]".format(end, start))
        return [start, end]


def parse_authorization(headers):
    if "Authorization" in headers:
        authorization = headers["Authorization"].split("Basic ")[-1]
        return b64d_and_utf8d(authorization).split(":")
    else:
        return []


def set_authenticate_response():
    from .core import set_status, set_header
    set_status(401)
    set_header("WWW-Authenticate", "Basic")


def _basic_authorization(headers, credentials: dict = None):
    if not credentials:
        credentials = {"admin": "admin"}
    if "Authorization" not in headers:
        set_authenticate_response()
        return False
    u, p = parse_authorization(headers)
    if u in credentials and credentials[u] == p:
        return True
    set_authenticate_response()
    return False


def _should_read_from_cache_file(fp: str, cache_fp: str, how_to_load):
    if os.path.isfile(fp):
        if os.path.isfile(cache_fp):
            cache = how_to_load(open(cache_fp, "rb").read())
            if "Last-Modified" in cache["headers"]:
                ims = rfc822gmt2dt(cache["headers"]["Last-Modified"])
                if ims:
                    lastmodified = math.floor(os.path.getmtime(fp))
                    lastmodified = datetime.datetime.fromtimestamp(lastmodified)
                    if ims >= lastmodified:
                        from .core import set_status, set_header, print_flush
                        set_status(cache["status_code"])
                        for k, v in cache["headers"].items():
                            set_header(k, v)
                        print_flush(cache["cache"])
                        return True


def _write_to_cache_file(cache, cache_fp: str = None, how_to_dump = None):
    if not (cache_fp and callable(how_to_dump)):
        return
    fp = cache_fp
    try:
        os.makedirs(os.path.dirname(fp))
    except:
        pass
    try:
        open(fp, "wb").write(how_to_dump(cache))
    except:
        pass


