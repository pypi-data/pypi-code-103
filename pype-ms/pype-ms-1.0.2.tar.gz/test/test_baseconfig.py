import os

import pytest
import yaml

from pype import BaseConfig

params = {"param": 1}
inputs = {"input": 1, "optional_input": 2}


def test_mockconfig_can_instantiate(tmpdir, MockConfig,):
    MockConfig(job_id="bla", pipeline_dir=tmpdir, params=params, inputs=inputs)


def test_mockconfig_can_has_attributes(tmpdir, MockConfig,):
    config = MockConfig(job_id="bla", pipeline_dir=tmpdir, params=params, inputs=inputs)

    for key in ["inputs", "params", "outputs", "job_id"]:
        assert key in config.config


def test_mockconfig_can_instantiate_twice(tmpdir, MockConfig,):
    MockConfig(job_id="foo", pipeline_dir=tmpdir, params=params, inputs=inputs)
    config = MockConfig(job_id="bar", pipeline_dir=tmpdir, params=params, inputs=inputs)

    assert config["outputs"]["result"].endswith("bar/output/result.ext")


def test_mock_config_creates_the_right_paths(tmpdir, MockConfig,):
    config = MockConfig(job_id="bla", pipeline_dir=tmpdir, params=params, inputs=inputs)

    assert os.path.exists(os.path.join(tmpdir, config["job_id"], "output"))
    assert os.path.exists(os.path.join(tmpdir, config["job_id"], "git_sha.txt"))
    assert os.path.exists(os.path.join(tmpdir, config["job_id"], "config.yaml"))


def test_cant_instantiate_when_missing_input(tmpdir, MockConfig,):
    with pytest.raises(RuntimeError):
        MockConfig(params=params, pipeline_dir=tmpdir, inputs=dict())


def test_cant_instantiate_with_unexpected_input(tmpdir, MockConfig,):
    with pytest.raises(RuntimeError):
        inputs_unexpected = dict({"unexpected_input": "2"}, **inputs)
        MockConfig(params=params, inputs=inputs_unexpected, pipeline_dir=tmpdir)


def test_cant_instantiate_with_unexpected_param(tmpdir, MockConfig,):
    with pytest.raises(RuntimeError):
        params_unexpected = dict({"unexpected_param": "2"}, **params)
        MockConfig(params=params_unexpected, inputs=inputs, pipeline_dir=tmpdir)


def test_cant_create_class_with_wrong_attributes(tmpdir, MockConfig,):
    class WrongConfig(BaseConfig):
        script_path = "script/path"
        wrong_name_for_inputs = {"hello"}

    with pytest.raises(AttributeError):
        WrongConfig(pipeline_dir=tmpdir)


def test_mockconfig_has_default_value_on_param(tmpdir, MockConfig,):
    config = MockConfig(job_id="bla", pipeline_dir=tmpdir, inputs=inputs)
    assert config['params']['param'] == 'default'

def test_mockconfig_has_none_on_optional_input(tmpdir, MockConfig,):
    config = MockConfig(job_id="bla", pipeline_dir=tmpdir, inputs={'input': 1})
    assert config['inputs']['optional_input'] is None

def test_no_params_config_can_instantiate(tmpdir, MockConfig,):
    class NoParamConfig(BaseConfig):
        script_path = 'test.py'
        inputs = {"msg"}
        outputs = {"processed": "processed_message.txt"}

    NoParamConfig(
        pipeline_dir=tmpdir,
        job_id = "test_job",
        inputs={"msg": "msg.txt"}
    )

def test_inheritance():
    class ConfigMixin():
        outputs = {"a": "A"}

    class Config(ConfigMixin, BaseConfig):
        script_path ="b"

    config = Config()
    assert config['outputs']
