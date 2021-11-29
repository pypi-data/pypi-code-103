import os

import pytest

from pype import BaseConfig
from pype import utils


@pytest.fixture
def MockConfig():
    class _MockConfig(BaseConfig):
        script_path = "/mock/path"
        params = {"param": "default"}
        inputs = {"input"}
        optional_inputs = {"optional_input"}
        outputs = {"result": "result.ext"}

    return _MockConfig


@pytest.fixture
def pipeline_dir(tmpdir, MockConfig):  # pylint: disable=redefined-outer-name
    MockConfig(job_id="A1", pipeline_dir=tmpdir, inputs={"input": 1}, tag="a")
    MockConfig(job_id="A2", pipeline_dir=tmpdir, inputs={"input": 1}, tag="a")
    MockConfig(job_id="B1", pipeline_dir=tmpdir, inputs={"input": 1}, tag="b")
    MockConfig(job_id="B2", pipeline_dir=tmpdir, inputs={"input": 1}, tag="b")
    utils.CONFIG_COLLECTOR.run(tmpdir)
    return tmpdir


@pytest.fixture
def pipeline_config(pipeline_dir): # pylint: disable=redefined-outer-name
    return os.path.join(pipeline_dir, 'pipeline_config.yaml')
