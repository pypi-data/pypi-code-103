# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.

"""
APIs for federated learning.
"""
from shrike import pipeline
from shrike.pipeline.pipeline_config import federated_config, silo
from shrike.pipeline.pipeline_helper import AMLPipelineHelper
from shrike._core import experimental
from coolname import generate_slug
from dataclasses import MISSING, dataclass
from typing import List, Any, Optional, Union
from azure.ml.component import dsl
from azure.ml.component.pipeline import Pipeline
from azure.ml.component.component import Component
import logging
from omegaconf import OmegaConf, open_dict, DictConfig

log = logging.getLogger(__name__)

EXPERIMENTAL_WARNING_MSG = (
    "Federated APIs are experimental and could change at any time."
)


def dataset_name_to_reference(
    component_instance: Component, dataset_names: list
) -> list:
    res = []
    if not dataset_names:
        return res
    for dataset in dataset_names:
        res.append(component_instance.outputs[dataset])
    return res


@dataclass
class StepOutput:
    step: Union[Component, Pipeline] = None
    outputs: List[str] = None


class FederatedPipelineBase(AMLPipelineHelper):
    @experimental(message=EXPERIMENTAL_WARNING_MSG)
    def create_base_name(self) -> str:
        """
        The training outputs from each silo will be stored at <base_name>/<silo_name> on the central storage.
        """
        rv = "fl-"
        rv += generate_slug(2)
        return rv

    @experimental(message=EXPERIMENTAL_WARNING_MSG)
    def preprocess(self, config: DictConfig, input: list) -> StepOutput:
        """
        Define the preprocess step. The outputs will be distributed to each silo's datastore.
        Return: a component/subgraph instance, and a list of output dataset name to be passed to the downstream pipeline **in order**
        """
        pass

    @experimental(message=EXPERIMENTAL_WARNING_MSG)
    def midprocess(self, config: DictConfig, input: list) -> StepOutput:
        """
        Define the midprocess step which reads outputs from `train` in each silo. The outputs will be distributed to each silo's datastore.
        Return: a component/subgraph instance, and a list of output dataset name to be passed to the downstream pipeline **in order**
        """
        pass

    @experimental(message=EXPERIMENTAL_WARNING_MSG)
    def postprocess(self, config: DictConfig, input: list) -> StepOutput:
        """
        Define the postprocess step which reads outputs from `train` in each silo and writes to the `noncompliant_datastore`.
        Return: a component/subgraph instance, and a list of output dataset name to be passed to the downstream pipeline **in order**.
        """
        pass

    @experimental(message=EXPERIMENTAL_WARNING_MSG)
    def train(self, config: DictConfig, input: list, silo: DictConfig) -> StepOutput:
        """
        Define the train step happening at each silo. This reads outputs from `preprocess` or `midprocess`, and sends outputs back to the `noncompliant_datastore`.
        Return: a component/subgraph instance, and a list of output dataset name to be passed to the downstream pipeline **in order**.
        """
        pass

    def data_transfer(
        self, input_list: list, destination_datastore: str, base_name: str
    ) -> list:
        # assume one shared ADF
        dts_name = self.config.federated_config.data_transfer_component
        try:
            data_transfer_component = self.component_load(
                dts_name  # this component is subject to change
            )
            log.info(f"Using {dts_name} as data transfer component.")
        except Exception as e:
            log.error(
                f"Please specify the data transfer component name registered in your workspace in module manifest and `federated_config.data_transfer_component` pipeline yaml."
            )
            raise (e)

        res = []
        if not input_list:
            return res
        for input in input_list:
            data_transfer_step = data_transfer_component(source_data=input)
            self.apply_smart_runsettings(data_transfer_step, datatransfer=True)
            data_transfer_step.outputs.destination_data.configure(
                datastore=destination_datastore,
                path_on_datastore=base_name + "/" + input.port_name,
            )
            res.append(data_transfer_step.outputs.destination_data)
        return res

    def _process_at_orchestrator(self, prev: StepOutput) -> list:
        if isinstance(prev.step, Pipeline):
            prev_output = list(prev.step.outputs.values())
        elif isinstance(prev.step, Component):
            self.apply_smart_runsettings(prev.step)
            prev_output = dataset_name_to_reference(prev.step, prev.outputs)
        else:
            raise Exception(
                f"The output of preprocess/midprocess/postprocess step must be a Pipeline object or a Component object. You are using {type(prev.step)}."
            )
        return prev_output

    def _merge_config(self):
        # override priority: default_config < customized shared config < per-silo setting
        # everything in customized shared config have equal priority
        federated_config = self.config.federated_config
        default_config = federated_config.config_group.get("default_config", {})
        for silo_name, silo_config in federated_config.silos.items():
            customized_config = {}
            if "inherit" in silo_config:
                for inherit_config in silo_config["inherit"]:
                    customized_config = OmegaConf.merge(
                        customized_config, federated_config.config_group[inherit_config]
                    )
            log.info(
                f"=== Original config for silo {silo_name}: {self.config.federated_config.silos[silo_name]}"
            )
            with open_dict(default_config):
                merge = OmegaConf.merge(default_config, customized_config)
            log.info(f"=== Shared config {merge}")
            with open_dict(self.config.federated_config.silos[silo_name]):
                self.config.federated_config.silos[silo_name] = OmegaConf.merge(
                    merge, silo_config
                )
                self.config.federated_config.silos[silo_name].pop("inherit", None)
            log.info(
                f"=== Merged config for silo {silo_name}: {self.config.federated_config.silos[silo_name]}"
            )

    @experimental(message=EXPERIMENTAL_WARNING_MSG)
    def train_in_silo_once(
        self, silo_name: str, silo: DictConfig, prev_output: list, cool_name: str
    ) -> list:
        data_transfer_output = self.data_transfer(
            input_list=prev_output,
            destination_datastore=silo.datastore,
            base_name=cool_name,
        )
        train_step = self.train(self.config, input=data_transfer_output, silo=silo)
        if isinstance(train_step.step, Pipeline):
            train_output = list(train_step.step.outputs.values())
        elif isinstance(train_step.step, Component):
            self.apply_smart_runsettings(
                train_step.step,
                target=silo.compute,
                datastore_name=silo.datastore,
            )
            train_output = dataset_name_to_reference(
                train_step.step, train_step.outputs
            )
        else:
            raise Exception(
                f"The output of train step must be a Pipeline object or a Component object. You are using {type(train_step.step)}"
            )

        silo_output = self.data_transfer(
            input_list=train_output,
            destination_datastore=self.config.compute.noncompliant_datastore,
            base_name=cool_name + "/" + silo_name,
        )
        return silo_output

    @experimental(message=EXPERIMENTAL_WARNING_MSG)
    def build(self, config: DictConfig):
        @dsl.pipeline()
        def pipeline_function():
            self._merge_config()
            prev = self.preprocess(self.config)
            prev_output = self._process_at_orchestrator(prev)

            for iter in range(self.config.federated_config.max_iterations):
                cool_name = self.create_base_name()
                midprocess_input = []
                for silo_name, silo in self.config.federated_config.silos.items():
                    train_output = self.train_in_silo_once(
                        silo_name, silo, prev_output, cool_name
                    )
                    midprocess_input += train_output

                prev = self.midprocess(self.config, input=midprocess_input)
                prev_output = self._process_at_orchestrator(prev)

            prev = self.postprocess(self.config, input=prev_output)
            prev_output = self._process_at_orchestrator(prev)

        return pipeline_function

    def pipeline_instance(self, pipeline_function, config):
        pipeline = pipeline_function()
        return pipeline
