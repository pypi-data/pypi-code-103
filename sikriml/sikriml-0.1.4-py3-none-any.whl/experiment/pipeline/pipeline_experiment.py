from typing import List, TypeVar

from azureml.core.workspace import Workspace
from azureml.pipeline.core import Pipeline, PipelineStep

from ..experiment_abs import ExperimentAbstract

T = TypeVar("T")


class PipelineExperiment(ExperimentAbstract[Pipeline]):
    steps: List[PipelineStep]

    def __init__(
        self,
        experiment_name: str,
        workspace: Workspace,
    ) -> None:
        super().__init__(experiment_name, workspace)

    def get_config(self) -> Pipeline:
        return Pipeline(self.workspace, self.steps)

    def append_step(self, step: PipelineStep):
        self.steps.append(step)
