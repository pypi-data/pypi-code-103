# -*- coding: utf-8 -*-
# @File    : http.py
# @Time    : 2021/11/26 4:13 下午

from datetime import date
from datetime import datetime
from decimal import Decimal
from typing import Any
from typing import Union

from flask import Response
from orjson import dumps
from orjson import JSONDecodeError
from orjson import loads
from orjson import OPT_PASSTHROUGH_DATETIME


def _default(o: Any) -> Union[str, int, float]:
    if isinstance(o, datetime):
        return o.isoformat(sep=" ")
    elif isinstance(o, date):
        return o.isoformat()
    elif isinstance(o, Decimal):
        return str(o)
    else:
        raise TypeError(o)


def json_dumps(data: Any) -> str:
    return dumps(data, option=OPT_PASSTHROUGH_DATETIME, default=_default).decode(
        "utf-8"
    )


def json_loads(s: bytes) -> Any:
    try:
        return loads(s)
    except JSONDecodeError:
        return


def json_response(
    data: Union[dict, list, str, int, float], status: int = 200, headers: dict = None
) -> Response:
    content = dumps(data, option=OPT_PASSTHROUGH_DATETIME, default=_default)
    return Response(
        content,
        status=status,
        mimetype="application/json; charset=utf-8",
        headers=headers,
    )
