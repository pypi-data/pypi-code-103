from enum import Enum


__all__ = 'json_encoder',


def json_encoder(e):
    if isinstance(e, set):
        return list(e)
    if isinstance(e, Enum):
        return str(e)
    else:
        raise TypeError(
            f'Object of type {e.__class__.__name__} is not serializable'
        )
