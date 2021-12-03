import typing as t

from ingots.tests.units.bootstrap import test_base

from ingot_redis.bootstrap import IngotRedisBaseBuilder

__all__ = ("IngotRedisBaseBuilderTestCase",)


class IngotRedisBaseBuilderTestCase(test_base.BaseBuilderTestCase):
    """Contains tests for the IngotRedisBuilder class."""

    tst_cls: t.Type = IngotRedisBaseBuilder
    tst_entity_name: str = "ingot_redis"
    tst_entity_name_upper: str = "INGOT_REDIS"
    tst_entity_name_class_name: str = "IngotRedis"
    tst_entity_description = ""
