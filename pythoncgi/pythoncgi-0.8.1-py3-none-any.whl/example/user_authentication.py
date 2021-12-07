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


# for apache:
# # CGIPassAuth on
# try GET http://127.0.0.1/user_authentication.py


init()
keystore = {
    "admin": "admin"
}


def get_validater():
    # using some key store backend like keyring
    def backend(username: str = None, password: str = None):
        if username not in keystore:
            set_authenticate_response()
            return False
        if password != keystore[username]:
            set_authenticate_response()
            return False
        return True
    return backend


def validate():
    backend = get_validater()
    authorization = parse_authorization(_HEADERS)
    _ = backend(*authorization)
    if _:
        if not _POST:
            print("<script>window.history.back();</script>")
    elif "logout" in authorization:
        print("<script>window.history.back();</script>")
    else:
        print("<h1>401 Unauthorized</h1>")
    return _


@execute(
    method="get",
    authentication=lambda: True,
    # authentication=basic_authorization(keystore)
)
def get():
    print("<p>Logged in credentials: {}</p>".format(parse_authorization(_HEADERS)))
    print("<form method='post' onsubmit='this.action=window.location.href.replace(window.location.hostname, \"admin:admin@\"+window.location.hostname);return true'><input type='submit' value='Login'/></form>")
    print("<form method='post' onsubmit='this.action=window.location.href.replace(window.location.hostname, \"logout@\"+window.location.hostname);return true'><input type='submit' value='Logout'/> (Press ESC to bypass popup dialogue)</form>")
    print("<form action='?test=authentication' method='post'><input type='submit' value='Try authentication in POST page'/> (Press ESC to bypass popup dialogue)</form>")


@execute(
    method="post",
    authentication=validate,
)
def post():
    if not _POST:
        return
    print("<p>If you see this, it means you are authenticated.</p>")
    print("<p>Try logout and visit this page again.</p>")


if __name__ == '__main__':
    main()

