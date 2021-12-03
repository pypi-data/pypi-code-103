from enum import Enum



def json_encoder(e):
    if isinstance(e, set):
        return list(e)
    if isinstance(e, Enum):
        return str(e)
    else:
        raise TypeError(
            f'Object of type {e.__class__.__name__} is not serializable'
        )
