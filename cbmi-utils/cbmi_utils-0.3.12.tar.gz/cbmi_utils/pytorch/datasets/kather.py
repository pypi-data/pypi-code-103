from pathlib import Path
from typing import Callable, Optional

from .h5_dataset import H5Dataset

# TODO how to handle multiple resolution? Could use different "from_avocado" methods but then the API will differ between classes.


class Kather96x96(H5Dataset):
    """
    Kather dataset, more information can be found at https://zenodo.org/record/1214456
    """

    def __init__(self, root: str, sub_set: str, transform: Optional[Callable] = None, transform_target: Optional[Callable] = None, num_samples: int = 1):
        assert sub_set in ['train', 'valid', 'test']

        super().__init__(data_path=Path(root) / f'{sub_set}.h5',
                         data_key='image',
                         target_path=Path(root) / f'{sub_set}.h5',
                         target_key='label',
                         transform=transform,
                         transform_target=transform_target,
                         num_samples=num_samples)

        self.classes = ['ADI', 'BACK', 'DEB', 'LYM', 'MUC', 'MUS', 'NORM', 'STR', 'TUM']

    @classmethod
    def from_avocado(cls, sub_set: str = 'train', transform: Optional[Callable] = None, transform_target: Optional[Callable] = None, num_samples: int = 1):
        return cls('/data/ldap/histopathologic/processed_read_only/Kather_H5/res96', sub_set, transform, transform_target, num_samples=num_samples)

    @staticmethod
    def normalization_values():
        # Calculated on the 'train' set
        mean = [0.7359, 0.5805, 0.7014]
        std = [0.2154, 0.2781, 0.2226]
        return mean, std


class Kather224x224(H5Dataset):
    """
    Kather dataset, more information can be found at https://zenodo.org/record/1214456
    """

    def __init__(self, root: str, sub_set: str, transform: Optional[Callable] = None, transform_target: Optional[Callable] = None, num_samples: int = 1):
        assert sub_set in ['train', 'valid', 'test']

        super().__init__(data_path=Path(root) / f'{sub_set}.h5',
                         data_key='image',
                         target_path=Path(root) / f'{sub_set}.h5',
                         target_key='label',
                         transform=transform,
                         transform_target=transform_target,
                         num_samples=num_samples)

        self.classes = ['ADI', 'BACK', 'DEB', 'LYM', 'MUC', 'MUS', 'NORM', 'STR', 'TUM']

    @classmethod
    def from_avocado(cls, sub_set: str = 'train', transform: Optional[Callable] = None, transform_target: Optional[Callable] = None, num_samples: int = 1):
        return cls('/data/ldap/histopathologic/processed_read_only/Kather_H5/res224', sub_set, transform, transform_target, num_samples=num_samples)

    @staticmethod
    def normalization_values():
        # Calculated on the 'train' set
        mean = [0.7357, 0.5804, 0.7013]
        std = [0.2261, 0.2857, 0.2297]
        return mean, std
    
