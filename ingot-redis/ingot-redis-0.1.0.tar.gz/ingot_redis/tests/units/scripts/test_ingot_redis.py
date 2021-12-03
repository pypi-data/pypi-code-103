import typing as t

from ingots.tests.units.scripts import test_base

from ingot_redis.scripts.ingot_redis import IngotRedisDispatcher

__all__ = ("IngotRedisDispatcherTestCase",)


class IngotRedisDispatcherTestCase(test_base.BaseDispatcherTestCase):
    """Contains tests for the IngotRedisDispatcher class and checks it."""

    tst_cls: t.Type = IngotRedisDispatcher
    tst_builder_name = "test"
