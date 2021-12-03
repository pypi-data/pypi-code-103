from .v1 import run_parser as v1_parser


__all__ = 'registry',


registry = {
    'v1': v1_parser,
}
