from operator import attrgetter
from typing import Callable


get_id = attrgetter('id')


def response_with_ordering(keys, items, getter: Callable = get_id):
    keys_map = {val: i for i, val in enumerate(keys)}

    return sorted(items, key=lambda item: keys_map[getter(item)])
