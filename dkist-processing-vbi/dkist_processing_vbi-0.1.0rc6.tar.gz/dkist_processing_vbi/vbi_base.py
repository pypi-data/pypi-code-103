from abc import ABC

from dkist_processing_common.tasks import ScienceTaskL0ToL1Base

from dkist_processing_vbi.models.constants import VbiBudName


class VbiScienceTask(ScienceTaskL0ToL1Base, ABC):
    @property
    def num_spatial_steps(self) -> int:
        return self.constants[VbiBudName.num_spatial_steps.value]
