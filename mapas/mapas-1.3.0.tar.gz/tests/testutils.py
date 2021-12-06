import math
from os import path

EPSILON = 1e-6

here = path.abspath(path.dirname(__file__))


class FakeRenderer:
    def __init__(self):
        self.calls = []

    def paste(self, *args, **kwargs):
        self.calls.append({
            'args': args,
            'kwargs': kwargs,
        })


class FakeSource:
    def __init__(self):
        self.tile_requests = []

    def get_tile_size(self):
        return 256

    def get_tile_png(self, *args, **kwargs):
        self.tile_requests.append({
            'args': args,
            'kwargs': kwargs,
        })

        with open(path.join(here, 'assets/null-tile-256.png'), 'rb') as pngfile:
            return pngfile.read()


def float_equals(a, b) -> bool:
    return math.fabs(a - b) < EPSILON
