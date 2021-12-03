from .v1 import parse as v1_parse


__all__ = 'registry',


registry = {
    'v1': v1_parse,
}
