import json
import os

import pytest

from superwise.models.task import Task
from superwise.models.version import Version
from tests import get_entities_fixture
from tests import get_sw
from tests import print_results


@pytest.mark.vcr()
def test_e2e_vcr():
    run_test_e2e()


def test_e2e_full():
    """
    No cassete, for real e2e tests
    """
    if os.environ.get("E2E_ENABLE"):
        run_test_e2e()
    else:
        print("E2E tests disables, skip")


def run_test_e2e():
    """
    1. task create
    2. version create
    version get (Wait)
    3. get dataentity
    3b. patch data entity
    4. activate the version
    """
    if not os.environ.get("E2E_ENABLE"):
        print("E2E tests disables, skip")
        return
    # create task
    sw = get_sw()
    inline_model_test = sw.task.create(
        Task(
            task_type_id=1,
            prediction=[
                {"value": 0, "is_default": 0, "description": "1"},
                {"value": 0, "is_default": 0, "description": "0"},
            ],
            title="inline title",
            task_description="inline tesk description",
            allow_prediction_update=True,
            fictive_label_mapper=[],
            monitor_delay=1,
            label=[
                {"value": 1, "is_default": 1, "description": "1"},
                {"value": 0, "is_default": 0, "description": "0"},
            ],
        )
    )

    print_results("created task object 1", inline_model_test.get_properties())
    assert inline_model_test.title == "inline title"
    task_id = inline_model_test.task_id

    # create segment
    """ FIXME KEY ERROR
    segment = sw.task.create_segment(
        task_id,
        name="Segment A",
        definition=[{"feature": "binary_str_null", "condition": ["in"], "value": ["0", "1"]}],
    )
    """

    ## create version
    entities = get_entities_fixture()

    for e in entities:
        print(e.get_properties())
    versionExternal = Version(
        task_id=task_id,
        version_name="test version",
        external_id=None,
        baseline_files=["gs://superwise-tools/integration_tests/basic/baseline_meta.parquet"],
        data_entities=entities,
    )

    model = sw.version.create(versionExternal)
    vid = model.id
    ### pooling results
    # model_after_polling = sw.version.get_by_id(vid)
    # print(model_after_polling)

    response = sw.version.activate(vid)
    # assert model.id == vid
    print(response.content)
    assert response.status_code == 204
