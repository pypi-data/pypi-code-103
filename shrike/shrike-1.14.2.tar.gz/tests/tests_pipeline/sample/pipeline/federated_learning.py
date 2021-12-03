# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.

"""
Federated Learning Example.
"""
from shrike.pipeline import FederatedPipelineBase, StepOutput
import os, sys

SAMPLE_ROOT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if SAMPLE_ROOT_PATH not in sys.path:
    print(f"Adding to path: {SAMPLE_ROOT_PATH}")
    sys.path.append(str(SAMPLE_ROOT_PATH))

from subgraph.passthrough_subgraph import PassthroughSubgraph


class SampleFederatedPipeline(FederatedPipelineBase):
    @classmethod
    def required_subgraphs(cls):
        return {"DemoSubgraph": PassthroughSubgraph}

    def preprocess(self, config):
        func = self.component_load("stats_passthrough")
        pipeline_input_dataset = self.dataset_load(
            name=config.democomponent.input_data,
            version=config.democomponent.input_data_version,
        )
        step = func(input_path=pipeline_input_dataset)
        return StepOutput(step, ["output_path"])

    def train(self, config, input, silo):
        func = self.component_load("stats_passthrough")
        step = func(input_path=input[0])
        return StepOutput(step, ["output_path"])

    def midprocess(self, config, input):
        subgraph = self.subgraph_load("DemoSubgraph")
        step = subgraph(input[0])
        return StepOutput(step)

    def postprocess(self, config, input):
        func = self.component_load("stats_passthrough")
        step = func(input_path=input[0])
        return StepOutput(step, ["output_path"])


if __name__ == "__main__":
    SampleFederatedPipeline.main()
