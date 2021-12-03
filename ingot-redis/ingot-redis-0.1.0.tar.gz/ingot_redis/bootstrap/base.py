from logging import getLogger

from ingots.bootstrap.base import BaseBuilder

import ingot_redis as package

__all__ = ("IngotRedisBaseBuilder",)


logger = getLogger(__name__)


class IngotRedisBaseBuilder(BaseBuilder):

    package = package
