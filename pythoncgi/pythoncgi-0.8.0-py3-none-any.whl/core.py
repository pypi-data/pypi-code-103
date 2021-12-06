from .utils import obj_to_bytes, _should_return_304, _basic_authorization, _cache_control, parse_range, parse_authorization, set_authenticate_response, _write_to_cache_file, _should_read_from_cache_file
from omnitools import dt2yyyymmddhhmmss, HeadersDict, ApacheHeadersDict, str2html, encodeURIComponent
from http.cookies import SimpleCookie
import traceback as _traceback
from cgi import FieldStorage
import http.client
import mimetypes
import sys
import os


__SETTINGS = {
    "stdout": sys.stdout.buffer,
    "stderr": sys.stderr.buffer,
    "stdin": sys.stdin.buffer,
    "log_fp": "log.log",
    "log_format": lambda now, obj: now+b" "+obj,
    "buf_size": 65536,
    "default_content_type": {
        "Content-Type": "text/html; charset=utf-8"
    },
    "print_end": b"\n",
    "default_5xx_response": "<p>The server has no response regarding this error.</p>",
    "headers_filter": [
        "DOCUMENT_ROOT",
        "LANG",
        "CONTEXT_DOCUMENT_ROOT",
        "SERVER_SIGNATURE",
        "SERVER_SOFTWARE",
        "SERVER_PORT",
        "REMOTE_PORT",
        "SCRIPT_NAME",
        "SERVER_ADMIN",
        "LANGUAGE",
        "QUERY_STRING",
        "REDIRECT_QUERY_STRING",
        "GATEWAY_INTERFACE",
        "REQUEST_URI",
        "SERVER_PROTOCOL",
        "PYTHONIOENCODING",
        "SERVER_ADDR",
        "LC_ALL",
        "SCRIPT_FILENAME",
        "PATH",
        "CONTEXT_PREFIX",
    ],
}


def get_settings(k: str = None):
    if k:
        return __SETTINGS[k]
    else:
        return __SETTINGS


def update_settings(w):
    t = type(__SETTINGS[w])
    if type(w) is not t:
        raise TypeError("{} is not {}".format(type(w), t))
    __SETTINGS.update(w)


_SERVER = HeadersDict()
_GET = dict()
_POST = dict()
_SESSION = SimpleCookie()
_COOKIE = dict()
_HEADERS = ApacheHeadersDict()
__FLAGS = {
    "initialized": False,
    "printed": {
        "status": False,
        "headers": False,
    }
}
__RESPONSE = {
    "status_code": 200,
    "headers": {},
    "content": b"",
    "cache": b""
}
__RESPONSE["headers"].update(get_settings("default_content_type"))
__METHODS = {}


def init(*, keep_blank_values: bool = True, session: str = None, headers_filter: list = None):
    if __FLAGS["initialized"]:
        return
    if headers_filter:
        update_settings({"headers_filter", get_settings("headers_filter")+headers_filter})
    __SERVER = dict(os.environ)
    for k in list(__SERVER.keys()):
        if k.startswith("REDIRECT_"):
            __SERVER[k.replace("REDIRECT_", "")] = __SERVER[k]
    arguments = FieldStorage(environ=__SERVER, keep_blank_values=keep_blank_values)
    arguments = {k: [_.value for _ in arguments[k]] if isinstance(arguments[k], list) else arguments[k].value for k in arguments}
    _SERVER.update(__SERVER)
    _GET.update(arguments)
    _POST.update(arguments)
    if session:
        _SESSION.load(session)
    _COOKIE.update({k: v.value for k, v in SimpleCookie(_SERVER["HTTP_COOKIE"]).items()} if "HTTP_COOKIE" in _SERVER else {})
    _HEADERS.update({k: v for k, v in _SERVER.items() if k not in get_settings("headers_filter")})
    __FLAGS.update({"initialized": True})


def log(obj, fp: str = None):
    obj = obj_to_bytes(obj, html=False)
    now = dt2yyyymmddhhmmss().encode()
    open(fp or get_settings("log_fp"), "ab").write(get_settings("log_format")(now, obj)+b"\n")


def log_construct(fp: str = None):
    def _log(obj):
        return log(obj, fp)

    return _log


def set_status(code: int):
    if not __FLAGS["printed"]["status"]:
        __RESPONSE["status_code"] = code
    else:
        raise Exception("status_code printed: {}, {}".format(
            __FLAGS["printed"]["status"],
            __RESPONSE["status_code"])
        )


def set_header(k, v):
    __RESPONSE["headers"].update({k: v})


def flush():
    _generate_headers()
    _print(__RESPONSE["content"])
    if __FLAGS["cacheable"]:
        __RESPONSE["cache"] += __RESPONSE["content"]
    __RESPONSE["content"] = b""
    get_settings("stdout").flush()


def _print(obj):
    get_settings("stdout").write(obj_to_bytes(obj))


def print(obj = b"", end=get_settings("print_end")):
    obj = obj_to_bytes(obj)
    __RESPONSE["content"] += obj
    if end:
        end = obj_to_bytes(end)
        __RESPONSE["content"] += end


def traceback(tag_name: str = "code", style: str = "", limit=None, chain=True):
    return "<{tag} style='{}'>{}</{tag}>".format(
        style,
        str2html(_traceback.format_exc(limit, chain)),
        tag=tag_name
    )


def print_flush(c: bytes, buf: int = get_settings("buf_size"), end=get_settings("print_end")):
    def w(c):
        while c:
            yield c[:buf]
            c = c[buf:]
    for _ in w(c):
        print(_, b"")
        flush()
    print(end=end)


def print_file(fo, buf_size: int = get_settings("buf_size"), range = None):
    if not hasattr(fo, "tell") or not hasattr(fo, "read") or not hasattr(fo, "seek") or not hasattr(fo, "close"):
        raise IOError("{} is not file object".format(fo))
    if not range:
        fo.seek(0, 2)
        range = [0, fo.tell()-1]
    fo.seek(range[0])
    while True:
        buf = min(buf_size, range[1] + 1 - fo.tell())
        buffer = fo.read(buf)
        buf = None
        if not buffer:
            break
        print_flush(buffer, buf_size, b"")
        buffer = None
    fo.close()


def generate_range_headers(fp, disposition: str = "inline"):
    if not os.path.isfile(fp):
        set_status(404)
        raise FileNotFoundError
    range = [0, None]
    if "Range" in _HEADERS:
        _range = parse_range(_HEADERS)
        if _range:
            range = _range
    if isinstance(fp, str):
        try:
            fo = open(fp, "rb")
        except:
            set_status(500)
            raise IOError("cannot open file")
    else:
        fo = fp
        fp = fo.name
    filename = os.path.basename(fp)
    try:
        size = os.path.getsize(fp)
    except:
        try:
            size = fp.size
        except:
            set_status(500)
            raise ValueError("cannot get file size")
    if range[0] >= size:
        set_status(416)
        raise ValueError("start [{}] > file size [{}]".format(range[0], size))
    if not range[1] or range[1] >= size:
        range[1] = size-1
    if range[0] != 0 or range[1] < size-1:
        set_status(206)
    length = range[1]-range[0]+1
    try:
        filename.encode("ascii")
        filename = 'filename="{}"'.format(filename)
    except UnicodeEncodeError:
        filename = "filename*=utf-8''{}".format(encodeURIComponent(filename))
    set_header("Accept-Range", "bytes")
    set_header("Content-Type", mimetypes.guess_type(filename)[0] or "application/octet-stream")
    set_header("Content-Disposition", "{}; {}".format(disposition, filename))
    set_header("Content-Range", "bytes {}-{}/{}".format(range[0], range[1], size))
    set_header("Content-Length", str(length))
    return fo, range


def should_return_304(fp: str):
    def return_304():
        return _should_return_304(_HEADERS, fp)

    return return_304


def should_read_from_cache_file(fp: str = None, cache_fp: str = None, how_to_load = None):
    def read_cache():
        if not (fp and os.path.isfile(fp) and cache_fp and os.path.isfile(cache_fp) and callable(how_to_load)):
            return False
        _should_read_from_cache_file(fp, cache_fp, how_to_load)

    return read_cache


def write_to_cache_file(cache_fp: str = None, how_to_dump = None):
    def write_cache(cache):
        _write_to_cache_file(cache, cache_fp, how_to_dump)

    return write_cache


def basic_authorization(credentials: dict):
    # to be done: windows and unix based authentication
    # reference: pyftpdlib.authorizers
    def basic_auth():
        return _basic_authorization(_HEADERS, credentials)

    return basic_auth


def _generate_headers():
    if not __FLAGS["printed"]["status"]:
        _print("{}: {}\n".format("Status", __RESPONSE["status_code"]))
        __FLAGS["printed"]["status"] = True
    if not __FLAGS["printed"]["headers"]:
        for k, v in __RESPONSE["headers"].items():
            _print("{}: {}\n".format(k, v))
        session = _SESSION.output()
        if session:
            session += "\n"
        _print(session)
        _print("\n")
        __FLAGS["printed"]["headers"] = True


def _generate_response():
    _generate_headers()
    flush()
    _print(__RESPONSE.pop("content"))
    status_code = __RESPONSE["status_code"]
    if not __RESPONSE["cache"] and status_code >= 500 and status_code <= 599:
        if status_code in http.client.responses:
            msg = http.client.responses[status_code]
            status_message = "<h1>{} {}</h1><br/>{}".format(
                status_code,
                msg,
                get_settings("default_5xx_response")
            )
            _print(status_message)


def execute(
        method: str = "get", cacheable: bool = False,
        cache_ctrl = lambda: _cache_control(max_age=0, must_revalidate=True),
        cache_norm = should_return_304(None),
        cache_strat = should_read_from_cache_file(),
        cache_store = write_to_cache_file(),
        authentication = basic_authorization(None),
        enable_tb: bool = True, traceback_kwargs: dict = None
    ):
    __FLAGS.update({"cacheable": cacheable})
    def wrapper(method_main):
        limit = None
        chain = True
        try:
            limit = traceback_kwargs["limit"]
        except:
            pass
        try:
            chain = traceback_kwargs["chain"]
        except:
            pass
        def _execute():
            read_from_cache_file = False
            try:
                if authentication():
                    if cacheable:
                        cache_ctrl()
                    if cacheable:
                        if cache_norm():
                            set_status(304)
                        else:
                            read_from_cache_file = cache_strat()
                            if not read_from_cache_file:
                                method_main()
                    elif not cacheable:
                        method_main()
            except:
                log(_traceback.format_exc(limit, chain))
                __RESPONSE["headers"].update(get_settings("default_content_type"))
                if enable_tb:
                    tb = traceback(**(traceback_kwargs or {}))
                else:
                    tb = "<h1>500 Internal Server Error</h1><br/><p>HTML stack trace is disabled.<br/>Check traceback log.</p>"
                __RESPONSE["content"] = obj_to_bytes(tb)
                try:
                    set_status(500)
                except:
                    log(_traceback.format_exc())
            try:
                _generate_response()
                if not read_from_cache_file and cacheable and __RESPONSE["status_code"] == 200:
                    cache_store(__RESPONSE)
            except:
                log(_traceback.format_exc())
                try:
                    set_status(500)
                except:
                    log(_traceback.format_exc())
            finally:
                __RESPONSE.clear()

        __METHODS[method] = _execute
        return _execute

    return wrapper


def main(**kwargs):
    init(**kwargs)
    method = _SERVER["REQUEST_METHOD"].lower()
    if method in __METHODS:
        __METHODS[method]()
    else:
        set_status(405)

