"""
Unit tests for sys_toolkit.collection module
"""

import time

from sys_toolkit.collection import (
    CachedMutableMapping,
    CachedMutableSequence,
    ExpiringObjectCache,
)

TEST_ITEM = {
    'test': 'test item in cache'
}


# pylint: disable=too-few-public-methods
class MockCache(ExpiringObjectCache):
    """
    Mocked instance of ExpiringObjectCache object without data
    """
    __max_age_seconds__ = 0.5

    def update(self):
        self.__start_update__()
        self.__finish_update__()


class MockCachedMutableSequence(CachedMutableSequence):
    """
    Mocked instance of CachedMutableSequence with trivial update() method
    """
    __max_age_seconds__ = 0.2

    def update(self):
        """
        Mock update call
        """
        self.clear()
        self.__start_update__()
        self.append(TEST_ITEM)
        self.__finish_update__()


class MockCachedMutableMapping(CachedMutableMapping):
    """
    Mocked minimal instance of CachedMutableMapping with trivial update() method
    """
    __max_age_seconds__ = 0.2

    def update(self, other=(), /, **kwds):
        """
        Mock update call
        """
        self.__start_update__()
        self.clear()
        for key, value in TEST_ITEM.items():
            self[key] = value
        self.__finish_update__()


def test_expiring_object_cache():
    """
    Test ExpiringObjectCache minimal base class without actual data
    """
    obj = MockCache()
    for attr in ('__loaded__', '__load_duration__', '__load_start__'):
        assert getattr(obj, attr) is None
    assert obj.__loading__ is False
    assert obj.__requires_reload__ is True

    obj.update()
    assert obj.__requires_reload__ is False
    assert isinstance(obj.__loaded__, float)
    assert isinstance(obj.__load_duration__, float)
    assert obj.__load_start__ is None
    assert obj.__loading__ is False

    assert isinstance(obj.__max_age_seconds__, (int, float))
    time.sleep(obj.__max_age_seconds__)
    assert isinstance(obj.__loaded__, float)
    assert obj.__requires_reload__ is True

    obj.__max_age_seconds__ = None
    assert obj.__requires_reload__ is False

    obj.__loading__ = True
    assert obj.__requires_reload__ is False

    obj.__reset__()
    assert obj.__requires_reload__ is True

    obj.__finish_update__()
    assert obj.__requires_reload__ is False


def test_cached_mutable_mapping():
    """
    Test minimal child class of CachedMutableMapping
    """
    obj = MockCachedMutableMapping()
    assert obj.__requires_reload__ is True

    obj.update()
    assert obj.__requires_reload__ is False
    assert len(obj) == 1

    obj.__loaded__ = obj.__loaded__ - obj.__max_age_seconds__ * 2
    assert obj.__requires_reload__ is True
    assert len(obj) == 1

    keys = list(obj.keys())
    obj.__loaded__ = obj.__loaded__ - obj.__max_age_seconds__ * 2
    assert obj.__requires_reload__ is True
    for key in keys:
        assert obj[key] is not None

    obj.__loaded__ = obj.__loaded__ - obj.__max_age_seconds__ * 2
    assert obj.__requires_reload__ is True
    for key in obj:
        del obj[key]
    assert obj == {}


def test_cached_mutable_sequence():
    """
    Test minimal child class of CachedMutableSequence
    """
    obj = MockCachedMutableSequence()
    assert obj.__requires_reload__ is True

    obj.update()
    assert obj.__requires_reload__ is False

    obj.__loaded__ = obj.__loaded__ - obj.__max_age_seconds__ * 2
    assert obj.__requires_reload__ is True
    assert len(obj) == 1

    obj.__loaded__ = obj.__loaded__ - obj.__max_age_seconds__ * 2
    obj.__loaded__ = obj.__loaded__ - obj.__max_age_seconds__ * 2
    item = obj[0]

    assert item == TEST_ITEM
    del obj[0]

    obj.insert(0, item)
    obj.insert(0, item)
    obj[0] = ''
    assert obj[0] == ''
