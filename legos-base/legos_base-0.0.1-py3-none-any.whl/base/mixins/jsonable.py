import json
from collections import OrderedDict


class JsonType(type):
    """JsonType metaclass handles auto-registering all the derived classes
    from a JsonMixin base class. This allows us to handle decoding of nested
    hierarchies.
    """

    def __new__(cls, clsname, bases, clsdict):
        ncls = super().__new__(cls, clsname, bases, clsdict)
        if not hasattr(ncls, "_json_types"):
            ncls._json_types = OrderedDict()
        ncls._json_types[clsname] = ncls
        return ncls

    @property
    def json_types(cls):
        return cls._json_types


class JsonMixin(object, metaclass=JsonType):
    """Mixin class adding JSON serialization functionality to its derived classes.

    By default all of the attributes on the class instance will be serialized.
    If the subclass specifies and attribute names in the '_jsonfields' class attribute,
    then only those attributes will be serialized. Attribute in '_jsonexcludefields' will
    be ignored.

    If a subclass needs to override the encode and decode functionality, they can
    define these methods on the subclass itself.
    """

    _jsonfields = ()
    _jsonexcludefields = ()

    def encode(self, *args, **kwargs):
        """Encodes the instance into a JSON string.
        """
        return json.dumps(self, cls=ObjectEncoder, *args, **kwargs)

    @classmethod
    def decode(cls, jstr, *args, **kwargs):
        """Decodes a json string and returns the object as a class instance.
        """
        return json.loads(jstr, cls=ObjectDecoder, *args, **kwargs)


class ObjectEncoder(json.JSONEncoder):
    def __init__(self, fields=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields = fields

    def default(self, obj, *args, **kwargs):
        if issubclass(obj.__class__, JsonMixin):
            fields = obj.__class__._jsonfields
            exfields = obj.__class__._jsonexcludefields
            d = OrderedDict({"__classname__": obj.__class__.__name__})
            d.update(
                obj.__dict__
                if not fields and not exfields
                else {
                    k: v
                    for k, v in obj.__dict__.items()
                    if k in fields or k not in exfields
                }
            )
            return d
        return super().default(obj, *args, **kwargs)


class ObjectDecoder(json.JSONDecoder):
    def __init__(self, *args, **kwargs):
        super().__init__(object_hook=self.cdecode, *args, **kwargs)

    def cdecode(self, d, *args, **kwargs):
        ckey = "__classname__"
        if ckey in d:
            classname = d.pop(ckey)
            if classname in JsonMixin._json_types.keys():
                objclass = JsonMixin._json_types[classname]
                obj = objclass.__new__(objclass)
                fields = objclass._jsonfields
                exfields = objclass._jsonexcludefields
                _d = (
                    d
                    if not fields and not exfields
                    else {
                        k: v for k, v in d.items() if k in fields or k not in exfields
                    }
                )
                for k, v in _d.items():
                    setattr(obj, k, v)
                return obj
        return d
