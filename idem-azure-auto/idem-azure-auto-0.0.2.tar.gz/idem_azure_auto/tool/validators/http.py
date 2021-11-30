try:
    import validators

    HAS_LIBS = (True,)
except ImportError as e:
    HAS_LIBS = False, str(e)


def __virtual__(hub):
    return HAS_LIBS


# https://developer.mozilla.org/en-US/docs/Web/HTTP/Methods
SUPPORTED_HTTP_METHODS = {
    "GET",
    "HEAD",
    "POST",
    "PUT",
    "DELETE",
    "CONNECT",
    "OPTIONS",
    "TRACE",
    "PATCH",
}


def request_method(hub, http_method: str):
    if http_method is None or http_method.upper() not in SUPPORTED_HTTP_METHODS:
        raise ValueError(f"{http_method} is not a valid http request method.")


def url(hub, http_url: str):
    try:
        validators.url(http_url)
    except validators.ValidationFailure as e:
        raise ValueError(f"{http_url} is not a valid http url")
