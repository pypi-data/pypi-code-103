# pylint: disable=no-member
import os
import pprint
from uuid import uuid4

import yaml

from pype import utils


class BaseConfig:
    _expected_attribute_types = {
        "inputs": set,
        "optional_inputs": set,
        "script_path": str,
        "params": dict,
        "outputs": dict,
    }

    def __init__(
        self,
        pipeline_dir=None,
        job_id=None,
        inputs=None,
        params=None,
        wait_for=None,
        tag=None,
    ):
        """
        Inherit from this config class to create configs for jobs.

        class ExampleConfig(BaseConfig):
            script_path = 'path/to/script/that/configured/by/this/config'
            inputs = {'input_key'}
            params = {'param_key'}
            outputs = {'output_1': 'path/to/where_output_is_saved'}
            optional_inputs = {'optional_input'}

        script pth has to be set so that the config knows where to find the

        To set an optional parameter/input use the default value None.
            outputs has to be a dictionary as it is name of what to save and where to save it
            inputs and params are sets as the user has to specify themselves what there values re
            inputs are always paths to data or outputs from other jobs
            params are the parameters needed to run a job and does not necessarily come from
            outside

        To set an optional parameter/input use the default value None.
        """

        # Verify construcion of child
        assert hasattr(
            self, "script_path"
        ), f"Configuration class for f{type(self)} must include script_path"

        for attr_name in self._expected_attribute_types:
            if not hasattr(self, attr_name):
                setattr(self, attr_name, self._expected_attribute_types[attr_name]())

        self._verify_attributes()

        # Initialise config

        inputs = inputs if inputs else dict()
        params = params if params else dict()

        _verify_keys(inputs.keys(), self.inputs, self.optional_inputs)
        _verify_keys(params.keys(), set(), self.params.keys())

        job_id = str(uuid4()) if not job_id else job_id
        if not pipeline_dir:
            pipeline_dir = utils.get_pipeline_dir()
        job_dir = os.path.join(pipeline_dir, job_id)
        output_dir = os.path.join(job_dir, "output")

        outputs = dict()
        for key in self.outputs:
            outputs[key] = os.path.join(output_dir, self.outputs[key])

        self.config = {}
        self.config["script_path"] = self.script_path
        self.config["job_id"] = job_id
        self.config["job_dir"] = job_dir
        self.config["qualname"] = type(self).__qualname__
        if wait_for:
            self.config["wait_for"] = wait_for
        if tag:
            if isinstance(tag, list):
                self.config["tag"] = tag
            else:
                self.config["tag"] = [tag]

        for key in self.params:
            if key not in params:
                params[key] = self.params[key]

        for key in self.optional_inputs:
            if key not in inputs:
                inputs[key] = None

        for name, val in zip(
            ["params", "inputs", "outputs"], [params, inputs, outputs]
        ):
            if val:
                self.config[name] = val

        os.makedirs(output_dir, exist_ok=True)
        print(f"Created dirs for {job_id}: {os.path.join(job_dir, 'config.yaml')}")

        yaml.dump(self.config, open(os.path.join(job_dir, "config.yaml"), "w"))

        if utils.GIT_CONTROL:
            utils.save_git_sha(job_dir)

        utils.CONFIG_COLLECTOR.add_config(self.config)

    def _verify_attributes(self):
        attrs = set(filter(lambda x: not x.startswith("_"), dir(self)))
        unexpected_attributes = attrs - self._expected_attribute_types.keys()
        if unexpected_attributes:
            raise AttributeError(
                f"Got unexpected attributes {unexpected_attributes}, allowed "
                f"attributes are {self._expected_attribute_types}"
            )

        for attr in attrs:
            if attr in self._expected_attribute_types:
                assert isinstance(
                    getattr(self, attr), self._expected_attribute_types[attr]
                ), (
                    f"Attribute {attr} on {type(self)} should be of type "
                    f"{self._expected_attribute_types[attr]} but is instead of type"
                    f" {type(getattr(self,attr))}."
                )

    def __getitem__(self, key):
        return self.config[key]

    def __str__(self):
        return pprint.pformat(self.__dict__, indent=3)


def _verify_keys(data_keys, expected_keys, optional_keys):
    missing_keys = expected_keys - data_keys
    unexpected_keys = data_keys - expected_keys - optional_keys

    if missing_keys:
        raise RuntimeError(f"missing inputs/params: {missing_keys}")
    if unexpected_keys:
        raise RuntimeError(f"Got unexpected_keys inputs/params: {unexpected_keys}")
