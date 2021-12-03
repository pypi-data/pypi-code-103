from pathlib import Path
from typing import Callable, Optional

from .h5_dataset import H5Dataset

# TODO how to handle multiple resolution? Could use different "from_avocado" methods but then the API will differ between classes.


class Midog96x96(H5Dataset):
    """ 
    Midog dataset in resolution 96x96. Further information can be found at TODO
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
        
        self.classes = ['non_mitosis', 'mitosis']

    @classmethod
    def from_avocado(cls, sub_set: str = 'train', transform: Optional[Callable] = None, transform_target: Optional[Callable] = None, num_samples: int = 1):
        return cls('/data/ldap/histopathologic/processed_read_only/MIDOG_H5/96x96', sub_set, transform, transform_target, num_samples=num_samples)

    @staticmethod
    def normalization_values():
        # Calculated on the 'train' set
        mean = [0.7469, 0.5232, 0.6920]
        std = [0.1831, 0.1996, 0.1736]
        return mean, std


class Midog224x224(H5Dataset):
    """ 
    Midog dataset in resolution 224x224. Further information can be found at TODO
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
        
        self.classes = ['non_mitosis', 'mitosis']

    @classmethod
    def from_avocado(cls, sub_set: str = 'train', transform: Optional[Callable] = None, transform_target: Optional[Callable] = None, num_samples: int = 1):
        return cls('/data/ldap/histopathologic/processed_read_only/MIDOG_H5/224x224', sub_set, transform, transform_target, num_samples=num_samples)

    @staticmethod
    def normalization_values():
        # Calculated on the 'train' set
        mean = [0.7469, 0.5232, 0.6921]
        std = [0.1927, 0.2092, 0.1811]
        return mean, std
        