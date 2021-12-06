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
from omnitools import crc32hd, dt2rfc822gmt, rfc822gmt2dt
import datetime
import pickle
import math
import os


# try GET http://127.0.0.1/caching_101.py?get=test.html
# refresh to test 304
# and then edit test.html
# try GET again

init()


def get_cache_fp():
    # find a way to turn URL to an os friendly filename
    # # if the client request binds to a user session
    # # you need to append those info to the hash
    return os.path.join("_cache", crc32hd(_GET["get"])+".cache")


def how_to_load(cache):
    return pickle.loads(cache)


def how_to_dump(cache):
    return pickle.dumps(cache)


@execute(
    method="get",
    # you must not cache large files
    # otherwise this will consume disk space and memory
    cacheable=True,
    # when to and not to return 304 status
    # in this case should be comparing
    # "if modified since" value and "modified time" of the get file
    # # you need to implement this method if client request binds to a user session
    # # for serving static files, simply wrap this method under your custom norm method
    cache_norm=should_return_304(_GET["get"]),
    # when to and not to return the cached response
    # in this case should be comparing
    # "last modified" value of the cached response and "modified time" of the get file
    # # do not use this field if you just want 304 effect
    cache_strat=should_read_from_cache_file(fp=_GET["get"], cache_fp=get_cache_fp(), how_to_load=how_to_load),
    # dump the response to file if there is no cached response or ims value to compare with modified time of the get file
    # # do not use this field if you just want 304 effect
    cache_store=write_to_cache_file(cache_fp=get_cache_fp(), how_to_dump=how_to_dump),
)
def get():
    if "get" in _GET:
        # let's say you want to cache some generated HTML code for the public
        # and you do not want to generate it each time different clients request it
        print(open("template.html", "rb").read().decode().format(open(_GET["get"], "rb").read().decode()), end="")


if __name__ == "__main__":
    main()

