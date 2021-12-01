import os
from typing import Tuple, List, Union
import logging

import h5py
import numpy as np

from actomyosin_analyser.tools.experiment_configuration import ExperimentConfiguration
from actomyosin_analyser.pipelines._pipeline import Pipeline
from actomyosin_analyser.tools.experiment_iterator import GroupIterator
from actomyosin_analyser.pipelines.length_distribution import LengthDistribution

logger = logging.getLogger(__name__)


class SegmentLength(Pipeline):

    def __init__(
            self,
            experiment_configuration: ExperimentConfiguration,
            n_processes: int=1
    ):
        super().__init__(experiment_configuration)
        self._ld_pipeline = LengthDistribution(experiment_configuration, n_processes)

        self.output_files.update({
            "segment_length": os.path.join(experiment_configuration['SegmentLength'],
                                           'segment_length.h5')
        })

    def run_analysis(self, frames: np.ndarray) -> List[Tuple[np.ndarray, np.ndarray]]:
        return self.get_means_and_variances(frames)


    def _validate_configuration(self):
        assert "SegmentLength" in self.experiment_configuration

    def get_means_and_variances(self, frames) -> List[Tuple[np.ndarray, np.ndarray]]:
        means_vars = []
        for group in self.experiment_configuration.experiment_iterator.groups:
            means_vars.append(self._get_means_and_variances_for_group(group, frames))

        return means_vars

    def _get_means_and_variances_for_group(
            self,
            group: GroupIterator,
            frames: np.ndarray
    ) -> Tuple[np.ndarray, np.ndarray]:
        means, variances = [], []
        for f in frames:
            logger.info(f"At group {group.get_label_from_values()}, "
                        f"frame {f}.")
            mean, var = self._get_mean_and_variance_for_frame(group, f)
            means.append(mean)
            variances.append(var)
        return np.array(means), np.array(variances)

    def _get_mean_and_variance_for_frame(self, group: GroupIterator, frame: int) -> Tuple[float, float]:
        mean, var = self._load_mean_and_variance(
            group, frame
        )
        if mean is not None:
            return mean, var
        mean, var = self._compute_mean_and_variance(group, frame)
        self._save_mean_and_variance(group, frame, mean, var)
        return mean, var

    def _compute_mean_and_variance(
            self,
            group: GroupIterator,
            frame: int
    ) -> Tuple[float, float]:
        lengths = self._ld_pipeline.get_lengths_by_group(group, frame)
        return lengths.mean(), lengths.var()

    def _save_mean_and_variance(self, group: GroupIterator, frame: int,
                                mean: float, variance: float):
        group_label = group.get_label_from_values()
        with h5py.File(self.output_files['segment_length'], 'a') as f:
            if group_label in f:
                h5_group = f[group_label]
            else:
                h5_group = f.create_group(group_label)
            frame_group = h5_group.create_group(str(frame))
            frame_group['mean'] = np.array([mean])
            frame_group['variance'] = np.array([variance])

    def _load_mean_and_variance(
            self,
            group: GroupIterator,
            frame: int
    ) -> Union[Tuple[None, None], Tuple[float, float]]:
        fname = self.output_files['segment_length']
        if not os.path.exists(fname):
            return None, None
        group_label = group.get_label_from_values()
        with h5py.File(fname, 'r') as f:
            if group_label not in f:
                return None, None
            h5_group = f[group_label]
            sf = str(frame)
            if sf not in h5_group:
                return None, None
            frame_group = h5_group[sf]
            return frame_group['mean'][0], frame_group['variance'][0]
