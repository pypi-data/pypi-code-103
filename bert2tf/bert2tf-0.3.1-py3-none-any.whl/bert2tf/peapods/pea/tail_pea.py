import argparse

from . import BasePea
from ...logging.base import get_logger


class TailPea(BasePea):
    """the tail pea of the pod"""

    def __init__(self, args: 'argparse.Namespace'):
        super().__init__(args)

        if self.name != self.__class__.__name__.lower():
            self.name = f'{args.name}-tail'

        self.args.name = self.name

        self.logger = get_logger(self.name)

        self.is_tail_router = True
