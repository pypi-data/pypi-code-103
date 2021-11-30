import pytest

from superwise.controller.exceptions import *
from superwise.models.segment import Segment
from superwise.models.segment import SegmentCondition
from superwise.models.segment import SegmentConditionDefinition
from superwise.models.task import Task
from tests import get_sw
from tests import print_results

segment_id = None


@pytest.mark.vcr()
def test_create_segment_inline():
    sw = get_sw()
    inline_model_test = sw.segment.create(
        Segment(
            task_or_id=Task(id=1),
            name="My Segment #1",
            definition_or_json=[
                SegmentConditionDefinition(
                    entity_or_name="merchant_id",
                    condition=SegmentCondition.IN,
                    value=["Israel", "United States of America"],
                ),
                SegmentConditionDefinition(
                    entity_or_name="periodic_11634", condition=SegmentCondition.GREATER_THAN, value=0.5
                ),
            ],
        )
    )
    print_results("created segment object 1", inline_model_test.get_properties())
    assert inline_model_test.task_id == 1
    assert inline_model_test.name == "My Segment #1"
    assert inline_model_test.id is not None


@pytest.mark.vcr()
def test_create_segment():
    sw = get_sw()
    segment = Segment()
    global segment_id
    segment.task_id = 1
    segment.name = "My Segment #2"
    segment.definition_json = [
        {"entity_name": "merchant_id", "condition": "in", "value": ["Israel", "United States of America"]},
        {"entity_name": "periodic_11634", "condition": ">", "value": 0.5},
    ]
    new_segment_model = sw.segment.create(segment)
    print_results("created segment object 2", new_segment_model.get_properties())
    assert new_segment_model.name == "My Segment #2"
    assert new_segment_model.task_id == 1
    assert new_segment_model.id is not None
    segment_id = new_segment_model.id


@pytest.mark.vcr()
def test_get_segment():
    sw = get_sw()
    global segment_id
    print("segment_id = " + str(segment_id))
    model = sw.segment.get_by_id(segment_id)
    assert int(model.id) == segment_id


@pytest.mark.vcr()
def test_create_segment_incomplete_input():
    sw = get_sw()
    segment = Segment()
    with pytest.raises(SuperwiseValidationException):
        sw.segment.create(segment)
    with pytest.raises(SuperwiseValidationException):
        sw.segment.create(Segment(task_id=1, name="My Segment #3"))
