from urllib.parse import ParseResult, urlunparse, urlencode, quote
from contextlib import contextmanager
import base64
import datetime
import functools

from flask import current_app, abort
from flask.json import JSONEncoder

from .exception import CatchableException

class CustomJSONEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.date):
            return obj.isoformat()
        elif isinstance(obj, datetime.datetime):
            return obj.isoformat()
        return JSONEncoder.default(self, obj)

def now():
    return datetime.datetime.utcnow().replace(microsecond=0, tzinfo=datetime.timezone.utc)
