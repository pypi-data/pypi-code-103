from kafka_processor.enhanced_list import EnhancedList
import pytest


@pytest.fixture
def enhanced_list():
    return EnhancedList([1, 2, 3])


def test_get_last_index(enhanced_list):
    enhanced_list[1]

    assert enhanced_list.last_accessed_index == 1, (
        f"wrong value returned for 'last_accessed_index', expected: 1 found: {enhanced_list.last_accessed_index}"
    )


def test_get_last_index_on_iteration(enhanced_list):
    for item in enhanced_list:
        if item == 2:
            break

    assert enhanced_list.last_accessed_index == 1, (
        f"wrong value returned for 'last_accessed_index', expected: 1 found: {enhanced_list.last_accessed_index}"
    )
