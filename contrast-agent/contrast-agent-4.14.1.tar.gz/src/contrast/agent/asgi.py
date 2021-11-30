# -*- coding: utf-8 -*-
# Copyright © 2021 Contrast Security, Inc.
# See https://www.contrastsecurity.com/enduser-terms-0317a for more details.
from io import BytesIO
from contrast.agent import scope as scope_
from contrast.agent.assess.policy.analysis import skip_analysis
from contrast.agent.assess.policy.source_node import SourceNode
from contrast.agent.assess.policy.source_policy import cs__apply_source
from contrast.utils.decorators import fail_safely


# note: request method is not a source, per labs
# source types translated from environ sources in environ_tracker.py
SCOPE_SOURCES = {
    "path": "URI",
    "raw_path": "URI",
    "query_string": "QUERYSTRING",
    "root_path": "OTHER",
    "server": "OTHER",
    "client": "OTHER",
    "headers": "HEADER",
    "cookie": "COOKIE",  # not an actual scope element; we use this for headers[cookie]
}

SOURCE_DICT = {"module": "ASGI.scope", "instance_method": False, "target": "RETURN"}


@fail_safely("Failed to convert starlette request to environ dict")
async def starlette_request_to_environ(request):
    body = await _get_body_non_destructive(request)
    return _scope_to_environ(request.scope, body)


async def _get_body_non_destructive(request):
    """
    Get the request body without consuming the ASGI `receive` callable. This involves
    some trickery. We bank on the fact that we're in a starlette / fastAPI environment,
    which uses `call_next` for each successive middleware.

    In the general ASGI case, we will need to perform all of the work currently done in
    request.body(), then send our replaced_receive function to the next middleware or
    application when we call it.
    """
    body = await request.body()
    called = False

    async def replaced_receive():
        # On the first call, send the whole body
        # On successive calls, send the disconnect message
        nonlocal called
        if not called:
            called = True
            return {
                "type": "http.request",
                "body": body,
                "more_body": False,
            }
        return {"type": "http.disconnect"}

    request._receive = replaced_receive
    return BytesIO(body)


def _scope_to_environ(scope, body):
    """
    Convert an asgi `scope` into a wsgi `environ` dict

    Copied from https://github.com/django/asgiref/blob/main/asgiref/wsgi.py
    and modified to our needs
    """
    environ = {
        "REQUEST_METHOD": scope["method"],
        "SCRIPT_NAME": scope.get("root_path", "").encode("utf8").decode("latin1"),
        "PATH_INFO": scope["path"].encode("utf8").decode("latin1"),
        "QUERY_STRING": scope["query_string"].decode("ascii"),
        "SERVER_PROTOCOL": "HTTP/{}".format(scope["http_version"]),
        "wsgi.version": (1, 0),
        "wsgi.url_scheme": scope.get("scheme", "http"),
        "wsgi.input": body,
        "wsgi.errors": BytesIO(),
        "wsgi.multithread": True,
        "wsgi.multiprocess": True,
        "wsgi.run_once": False,
    }
    # Get server name and port - required in WSGI, not in ASGI
    if "server" in scope:
        environ["SERVER_NAME"] = scope["server"][0]
        environ["SERVER_PORT"] = str(scope["server"][1] or 80)
    else:
        environ["SERVER_NAME"] = "localhost"
        environ["SERVER_PORT"] = "80"

    if "client" in scope:
        environ["REMOTE_ADDR"] = scope["client"][0]

    # Go through headers and make them into environ entries
    for name, value in scope.get("headers", []):
        name = name.decode("latin1")
        if name == "content-length":
            corrected_name = "CONTENT_LENGTH"
        elif name == "content-type":
            corrected_name = "CONTENT_TYPE"
        else:
            corrected_name = "HTTP_{}".format(name.upper().replace("-", "_"))
        # HTTPbis say only ASCII chars are allowed in headers, but we latin1 just in
        # case
        value = value.decode("latin1")
        if corrected_name in environ:
            value = environ[corrected_name] + "," + value
        environ[corrected_name] = value
    return environ


def track_scope_sources(context, scope):
    """
    Iterate over the ASGI scope and explicitly track all relevant values. This is
    similar to the environ tracker. This function does not track the request body, which
    comes from the receive awaitable.

    There's an unfortunate possibility of starlette's request object having already
    cached some data from the scope dict. The easiest way around this would be to find
    and clear all of the places where starlette might save these variables. This could
    be avoided by going for an approach that's closer to pure ASGI instead of relying as
    much on starlette.

    @param context: the current request context
    @param scope: the ASGI scope dict
    """
    if skip_analysis(context):
        return

    with scope_.contrast_scope():
        for key, value in scope.items():
            if key in ["client", "server"]:
                for elem in value:
                    _track_scope_item(context, scope, key, elem)
            elif key == "headers":
                for header_key, header_value in value:
                    if header_key == b"cookie":
                        key = "cookie"
                    _track_scope_item(context, scope, key, header_key)
                    _track_scope_item(context, scope, key, header_value)
            else:
                _track_scope_item(context, scope, key, value)


def _track_scope_item(context, scope, key, value):
    # there are other elements in `scope`, but only those in SCOPE_SOURCES matter to us
    if key in SCOPE_SOURCES:
        node = _build_source_node(key, SCOPE_SOURCES[key])
        cs__apply_source(context, node, value, scope, value, (), {}, source_name=key)


def _build_source_node(method_name, source_type):
    source_dict = SOURCE_DICT.copy()

    # headers (including cookies) should not trigger XSS, per labs
    tags = (
        ["CROSS_SITE"] if source_type not in ["HEADER", "COOKIE"] else ["NO_NEWLINES"]
    )

    source_dict["method_name"] = method_name
    source_dict["type"] = source_type
    source_dict["tags"] = tags

    node = SourceNode.from_dict("ASGI", source_dict)
    node.skip_stacktrace = True

    return node
