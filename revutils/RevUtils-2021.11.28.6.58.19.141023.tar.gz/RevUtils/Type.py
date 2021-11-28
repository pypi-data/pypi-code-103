from collections.abc import Generator


def is_generator(f):
    return isinstance(f, Generator)
