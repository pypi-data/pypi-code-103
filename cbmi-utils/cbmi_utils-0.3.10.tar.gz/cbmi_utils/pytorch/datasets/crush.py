from pathlib import Path
from typing import Callable, Optional

from .h5_dataset import H5Dataset


class Crush96x96(H5Dataset):
    """
    Data and further information can be found at TODO
    """

    def __init__(self, root: str, sub_set: str, transform: Optional[Callable] = None, transform_target: Optional[Callable] = None, num_samples: int = 1):
        assert sub_set in ['train', 'valid', 'test']

        super().__init__(data_path=Path(root) / f'{sub_set}.h5',
                         data_key='image',
                         target_path=Path(
                             root) / f'{sub_set}.h5',
                         target_key='label',
                         transform=transform,
                         transform_target=transform_target,
                         num_samples=num_samples)

        self.classes = ['C', 'T']  # C=crush and T=tumor

    @classmethod
    def from_avocado(cls, sub_set: str = 'train', transform: Optional[Callable] = None, transform_target: Optional[Callable] = None, num_samples: int = 1):
        return cls('/data/ldap/histopathologic/processed_read_only/Crush_96', sub_set, transform, transform_target, num_samples=num_samples)

    @staticmethod
    def normalization_values():
        # Calculated on the 'train' set
        mean = [0.9031, 0.6317, 0.7814]
        std = [0.1185, 0.1722, 0.1203]
        return mean, std
