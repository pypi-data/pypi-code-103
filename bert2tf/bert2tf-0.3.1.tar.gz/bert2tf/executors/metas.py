from typing import Dict

_defaults = None


def get_default_metas() -> Dict:
    """Get a copy of default meta variables"""
    import copy

    global _defaults

    if _defaults is None:
        from ..baml import BAML
        from pkg_resources import resource_stream
        with resource_stream('bert2tf', '/'.join(('resources', 'executors.metas.default.yml'))) as fp:
            _defaults = BAML.load(fp)

    return copy.deepcopy(_defaults)


def fill_metas_with_defaults(d: Dict) -> Dict:
    """Fill the incomplete ``metas`` field with complete default values

    :param d: the loaded YAML map
    """

    default_metas = get_default_metas()

    for key, value in d.items():
        if key not in default_metas:
            raise KeyError(f'{key} is not metas parameters.')
        else:
            default_metas[key] = value

    return default_metas
