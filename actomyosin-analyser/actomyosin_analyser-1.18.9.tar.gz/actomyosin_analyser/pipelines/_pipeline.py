from abc import ABC, abstractmethod
import os

from ..tools.experiment_configuration import ExperimentConfiguration


class Pipeline(ABC):

    def __init__(self, experiment_configuration: ExperimentConfiguration):
        self.experiment_configuration = experiment_configuration
        self._validate_configuration()
        self.plot_files = {}
        self.input_files = {}
        self.output_files = {}

    def __call__(self, *args, **kwargs):
        return self.run_analysis(*args, **kwargs)

    @abstractmethod
    def run_analysis(self, *args, **kwargs):
        ...

    @abstractmethod
    def _validate_configuration(self):
        ...

    def _remove_output_files(self):
        for key in self.output_files:
            f = self.output_files[key]
            if os.path.exists(f) and os.path.isfile(f):
                os.remove(f)