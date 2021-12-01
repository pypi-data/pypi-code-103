import os
from typing import List, Union

import h5py
import numpy as np

from ._pipeline import Pipeline
from ..tools.experiment_configuration import ExperimentConfiguration
from ..tools.experiment_iterator import GroupIterator




class Time(Pipeline):

    def run_analysis(self) -> List[np.ndarray]:
        times = []
        for g in self.experiment_configuration.experiment_iterator:
            time = self.get_time(g)
            times.append(time)
        return times


    def _validate_configuration(self):
        assert "Time" in self.experiment_configuration

    def __init__(self, experiment_configuration: ExperimentConfiguration):
        super().__init__(experiment_configuration)
        self.output_files.update({
            "Time": os.path.join(experiment_configuration["Time"], 'time.h5')
        })

    def get_time(self, group: GroupIterator) -> np.ndarray:
        time = self._load_time(group)
        if time is not None:
            return time

        time = Time._get_group_time(group)
        group_label = group.get_label_from_values()
        self._save_time(group_label, time)
        return time

    @staticmethod
    def _get_group_time(group: GroupIterator) -> np.ndarray:
        times = []
        for sim in group:
            a = sim.analyser
            time = a.get_time()
            times.append(time)
        as_array = np.vstack(times)
        if (as_array != as_array[0]).any():
            raise RuntimeError(f"Can't get time for group '{group.values}'. "
                               "Time axes are not identical. Use custom code to read "
                               "time axes of your experiment.")
        return as_array[0]

    def _load_time(self, group: GroupIterator) -> Union[np.ndarray, None]:
        group_label = group.get_label_from_values()
        filename = self.output_files["Time"]
        if not os.path.exists(filename):
            return None
        with h5py.File(filename, 'r') as f:
            if group_label not in f:
                return None
            time = f[group_label][:]
            return time

    def _save_time(self, group_label: str, time: np.ndarray):
        filename = self.output_files["Time"]
        with h5py.File(filename, 'a') as f:
            f[group_label] = time

