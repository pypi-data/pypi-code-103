from .hierarchical_v1 import run_parser as h_v1_runner, parse as h_v1_parse
from .v1 import run_parser as v1_runner, parse as v1_parse


__all__ = 'registry', 'raw_parsers',

registry = {
    'hierarchical_v1': h_v1_runner,
    'v1': v1_runner,
}
raw_parsers = {
    'hierarchical_v1': h_v1_parse,
    'v1': v1_parse,
}
