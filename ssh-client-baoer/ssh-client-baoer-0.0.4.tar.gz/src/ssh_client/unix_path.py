from typing import Text


def join(path: Text, *paths):
    return '/'.join([path.rstrip('/')] + list(map(lambda p: p.strip('/'), paths)))
