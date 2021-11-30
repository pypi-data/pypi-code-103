import dataclasses

from dataclasses_jsonschema import JsonSchemaMixin


def dataclass(cls=None, **kwargs):
    """A dataclass wrapper that ensures all dataclasses inherit JsonSchemaMixin"""

    def wrap(cls):
        new_cls = type(cls.__name__, (cls, JsonSchemaMixin), dict(cls.__dict__))
        return dataclasses.dataclass(new_cls, **kwargs)

    # See if we're being called as @dataclass or @dataclass().
    if cls is None:
        return wrap

    # We're called as @dataclass without parens.
    return wrap(cls)
