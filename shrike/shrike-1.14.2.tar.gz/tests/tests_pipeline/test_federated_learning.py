# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.

"""
PyTest suite for testing federated learning APIs.
"""
import pytest
import os
from functools import lru_cache
from omegaconf import OmegaConf
from pathlib import Path
from azureml.core.dataset import Dataset
from azureml.core import Datastore
from shrike.pipeline.federated_learning import (
    dataset_name_to_reference,
    FederatedPipelineBase,
)


@lru_cache(maxsize=None)
def federated_base():
    """
    Initiate AMLPipelineHelper class with the testing configuration.
    """
    config = OmegaConf.load(Path(__file__).parent / "data/test_configuration.yaml")
    rv = FederatedPipelineBase(config=config)
    rv.connect()
    return rv


def test_dataset_name_to_reference():
    module_instance = federated_base().component_load("stats_passthrough")
    step_instance = module_instance(input_path="foo")
    federated_base().apply_smart_runsettings(step_instance)
    outputs = dataset_name_to_reference(step_instance, ["output_path"])
    assert step_instance.outputs.output_path == outputs[0]


def test_data_transfer_without_dts_name(caplog):
    config = OmegaConf.load(Path(__file__).parent / "data/test_configuration.yaml")
    config.federated_config.data_transfer_component = ""
    fl_base = FederatedPipelineBase(config=config)
    fl_base.connect()
    with pytest.raises(Exception):
        fl_base.data_transfer([], "fake_compliant_datastore", "base_name")
    assert (
        "Please specify the data transfer component name registered in your workspace in module manifest and `federated_config.data_transfer_component` pipeline yaml."
        in caplog.text
    )


def test_data_transfer():
    fl_base = federated_base()
    stats_passthrough = fl_base.component_load("stats_passthrough")
    prev_step = stats_passthrough(input_path="foo")
    fl_base.apply_smart_runsettings(prev_step)
    base_name = fl_base.create_base_name()
    output = fl_base.data_transfer(
        [prev_step.outputs.output_path], "fake_compliant_datastore", base_name
    )[0]
    assert output.datastore == "fake_compliant_datastore"
    assert (
        output._dataset_output_options.path_on_datastore
        == base_name + "/" + "output_path"
    )


def test_process_at_orchestrator(caplog):
    fl_base = federated_base()
    with pytest.raises(Exception):
        fl_base._process_at_orchestrator("string")


def test_merge_config():
    fl_base = federated_base()
    fl_base._merge_config()
    config = fl_base.config.federated_config
    assert config.max_iterations == 2
    assert config.silos.silo1 == OmegaConf.create(
        {
            "compute": "fl-wus",
            "datastore": "fl_wus",
            "params": {"msg": "shared msg", "dataset": "test_uploaded_from_local"},
        }
    )
    assert config.silos.silo2 == OmegaConf.create(
        {
            "compute": "fl-eus",
            "datastore": "fl_eus",
            "params": {"msg": "shared msg", "dataset": "test_csv"},
        }
    )
    assert config.silos.silo3 == OmegaConf.create(
        {
            "compute": "fl-canada",
            "datastore": "fl_canada",
            "params": {"msg": "per-silo msg", "dataset": "test_csv"},
        }
    )
