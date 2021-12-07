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


# try GET http://127.0.0.1/basic_python_cgi.py?test=hi

init(
    # init kwargs, please refer to the corresponding object
    # FieldStorage(..., keep_blank_values=keep_blank_values)
    keep_blank_values=True,
    # _SESSION: SimpleCookie = SimpleCookie(session)
    session=None,
    # __SETTINGS["headers_filter"].extend(headers_filter)
    headers_filter=[
        "X_CLIENT_IP",
    ],
)
default_logger = log # to file "log.log"
mylogger = log_construct(fp="my.log")
default_logger({"hello"})
mylogger(obj=["hi"])


@execute(
    method="get",
    enable_tb=True,
    traceback_kwargs={
        "limit": None,
        "chain": True,
        "tag_name": "p",
        "style": "font-family: monospace; font-size: 3vh",
    },
    authentication=lambda: True,
)
def get():
    # status code
    # https://developer.mozilla.org/en-US/docs/Web/HTTP/Status
    set_status(500)

    # set response header
    # https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers
    set_header("Cache-Control", "max-age=0, must-revalidate")
    # from pythoncgi.utils import _cache_control
    # set_header("Cache-Control", _cache_control(max_age=0, must_revalidate=True))

    # set response cookie
    # https://developer.mozilla.org/en-US/docs/Web/HTTP/Cookies
    # https://docs.python.org/3.6/library/http.cookies.html
    _SESSION["its"] = "working"
    # python < 3.8 does not support SameSite attribute
    # manipulate the coded_value instead
    _SESSION["its"].set("its", "working", "working; SameSite=Lax")

    # debug, change internal settings
    update_settings({"print_end": b"\n<br/>\n"})
    print(get_settings()) # print_end is changed, check source code

    # set response body
    # similar to print, but only accepts two arguments
    # convert obj to bytes and save in memory
    # this will escape HTML entities automatically
    # either encode your data first or let it dump to HTML
    print(
        obj={
            "_SERVER": dict(_SERVER),
            "_HEADERS": dict(_HEADERS),
            "_COOKIE": _COOKIE,
            "_SESSION": _SESSION.output(),
            "_GET": _GET,
            "_POST": _POST,
        },
        end=b"<br>\n"
    )

    # flush memory to response stream
    # useful for printing binary files
    # this will prevent changes to response header
    flush()

    # dump a file to response stream, print content as is
    # must be in 'b' mode
    print("<textarea>", end="")
    # make sure to use print(b"something", end=None) when printing binary
    # otherwise there is a newline character after each print()
    print_file(
        fo=open("my.log", "rb"),
        buf_size=16*1024, # 16 KB
        range=None # None means all of it
        # to print partial content: pass a list with start and end value
        # values are inclusive, to print first 8 bytes: range=[0, 7]
    )
    print("</textarea>", end="")


if __name__ == '__main__':
    main()

