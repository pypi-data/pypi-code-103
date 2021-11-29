import datetime
import decimal
import json
import uuid
from json import JSONDecodeError, JSONDecoder  # noqa
from typing import Any, IO, Union

from dimtim.interfaces import Serializable
from dimtim.utils import duration, timezone

__all__ = [
    'dump', 'dumps', 'load', 'loads', 'JSONEncoder', 'JSONDecoder', 'JSONDecodeError'
]

compat_transforms = {}

try:
    from django.utils.functional import Promise

    compat_transforms[Promise] = lambda o: str(o)
except ImportError:
    pass

try:
    from pydantic import BaseModel

    compat_transforms[BaseModel] = lambda o: o.dict()
except ImportError:
    pass


class JSONEncoder(json.JSONEncoder):
    def __init__(self, **kwargs):
        kwargs.setdefault('ensure_ascii', False)
        super().__init__(**kwargs)

    def default(self, o):
        if isinstance(o, datetime.datetime):
            r = o.isoformat()
            if o.microsecond:
                r = r[:23] + r[26:]
            if r.endswith('+00:00'):
                r = r[:-6] + 'Z'
            return r

        if isinstance(o, datetime.date):
            return o.isoformat()

        if isinstance(o, datetime.time):
            if timezone.is_aware(o):
                raise ValueError('JSON can\'t represent timezone-aware times.')
            r = o.isoformat()
            if o.microsecond:
                r = r[:12]
            return r

        if isinstance(o, datetime.timedelta):
            return duration.duration_iso_string(o)

        if isinstance(o, (decimal.Decimal, uuid.UUID)):
            return str(o)

        if isinstance(o, Serializable):
            return o.serialize()

        for t, fn in compat_transforms.items():
            if isinstance(o, t):
                return fn(o)

        return super().default(o)


def load(fp: IO, **kwargs) -> None:
    return json.load(fp, **kwargs)


def loads(data: Union[str, bytes], **kwargs) -> Any:
    return json.loads(data, **kwargs)


def dump(obj: Any, fp: IO, **kwargs) -> None:
    kwargs.setdefault('cls', JSONEncoder)
    return json.dump(obj, fp, **kwargs)


def dumps(obj: Any, **kwargs) -> str:
    kwargs.setdefault('cls', JSONEncoder)
    return json.dumps(obj, **kwargs)
