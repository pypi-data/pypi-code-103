__all__ = [
    '_missing', '_MissingType',
    'JsonFormatError'
]


class _missing:
    pass


_MissingType = type[_missing]


class JsonFormatError(ValueError):
    pass
