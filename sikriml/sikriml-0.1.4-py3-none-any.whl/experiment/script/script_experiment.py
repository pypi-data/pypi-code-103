from abc import abstractmethod
from typing import TypeVar

from azureml.core import ScriptRunConfig
from azureml.core.workspace import Workspace

from ..experiment_abs import ExperimentAbstract

T = TypeVar("T")


class ScriptExperiment(ExperimentAbstract[ScriptRunConfig]):
    def __init__(
        self,
        experiment_name: str,
        workspace: Workspace,
    ) -> None:
        super().__init__(experiment_name, workspace)

    @abstractmethod
    def get_config(self) -> ScriptRunConfig:
        pass
