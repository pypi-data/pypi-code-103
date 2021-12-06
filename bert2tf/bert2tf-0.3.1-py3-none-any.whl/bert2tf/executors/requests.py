from typing import Dict, List

_defaults = {}


def get_default_reqs(cls_mro: List[type]) -> Dict:
    """Get a copy of default meta variables

    :param cls_mro: the MRO inherited order followed.
    """
    import copy

    global _defaults
    from ..baml import BAML

    for cls in cls_mro:
        try:
            if cls.__name__ not in _defaults:
                from pkg_resources import resource_stream
                with resource_stream('bert2tf', '/'.join(('resources', f'executors.requests.{cls.__name__}.yml'))) as fp:
                    _defaults[cls.__name__] = \
                        BAML.load(fp)  # do not expand variables at here, i.e. DO NOT USE expand_dict(yaml.load(fp))

            if cls.__name__ != cls_mro[0].__name__:
                from ..logging import default_logger
                default_logger.debug(f'"requests.on" setting of {cls_mro[0]} fallback to general {cls} setting, '
                                     f'because you did not specify {cls_mro[0]}')
            return copy.deepcopy(_defaults[cls.__name__])
        except FileNotFoundError:
            pass

    raise ValueError('not able to find any default settings along this chain %r' % cls_mro)
