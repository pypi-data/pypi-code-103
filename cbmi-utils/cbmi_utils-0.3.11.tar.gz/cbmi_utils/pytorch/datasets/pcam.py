from pathlib import Path
from typing import Callable, Optional

from .h5_dataset import H5Dataset


class PatchCamelyon(H5Dataset):
    """
    Data and further information can be found at https://humanunsupervised.github.io/humanunsupervised.com/pcam/pcam-cancer-detection.html
    """

    def __init__(self, root: str, sub_set: str, transform: Optional[Callable] = None, transform_target: Optional[Callable] = None, num_samples: int = 1):
        assert sub_set in ['train', 'valid', 'test']

        super().__init__(data_path=Path(root) / f'camelyonpatch_level_2_split_{sub_set}_x.h5',
                         data_key='x',
                         target_path=Path(
                             root) / f'camelyonpatch_level_2_split_{sub_set}_y.h5',
                         target_key='y',
                         transform=transform,
                         transform_target=transform_target,
                         num_samples=num_samples)

        self.classes = ['no_tumor', 'tumor']

    @classmethod
    def from_avocado(cls, sub_set: str = 'train', transform: Optional[Callable] = None, transform_target: Optional[Callable] = None, num_samples: int = 1):
        return cls('/data/ldap/histopathologic/original_read_only/PCam/PCam', sub_set, transform, transform_target, num_samples=num_samples)

    @staticmethod
    def normalization_values():
        # Calculated on the 'train' set
        mean = [0.7008, 0.5384, 0.6916]
        std = [0.2349, 0.2772, 0.2128]
        return mean, std
