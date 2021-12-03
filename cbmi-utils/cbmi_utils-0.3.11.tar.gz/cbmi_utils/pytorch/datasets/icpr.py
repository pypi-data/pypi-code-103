from pathlib import Path
from typing import Callable, Optional

from .h5_dataset import H5Dataset

# TODO how to handle multiple resolution? Could use different "from_avocado" methods but then the API will differ between classes.


class ICPR96x48Balanced(H5Dataset):
    """ 
    Data and further information can be found at TODO
    """

    def __init__(self, root: str, sub_set: str, transform: Optional[Callable] = None, transform_target: Optional[Callable] = None, num_samples: int = 1):
        assert sub_set in ['train', 'valid', 'test']

        super().__init__(data_path=Path(root) / f'{sub_set}/icpr_96_48_balanced.h5',
                         data_key='image',
                         target_path=Path(
                             root) / f'{sub_set}/icpr_96_48_balanced.h5',
                         target_key='label',
                         transform=transform,
                         transform_target=transform_target,
                         num_samples=num_samples)

    @classmethod
    def from_avocado(cls, sub_set: str = 'train', transform: Optional[Callable] = None, transform_target: Optional[Callable] = None, num_samples: int = 1):
        return cls('/data/ldap/histopathologic/processed/icpr_mitosis/', sub_set, transform, transform_target, num_samples=num_samples)


class ICPR96x48Unbalanced(H5Dataset):
    """ 
    Data and further information can be found at TODO
    """

    def __init__(self, root: str, sub_set: str, transform: Optional[Callable] = None, transform_target: Optional[Callable] = None, num_samples: int = 1):
        assert sub_set in ['train', 'valid', 'test']

        super().__init__(data_path=Path(root) / f'{sub_set}/icpr_96_48_unbalanced.h5',
                         data_key='image',
                         target_path=Path(
                             root) / f'{sub_set}/icpr_96_48_unbalanced.h5',
                         target_key='label',
                         transform=transform,
                         transform_target=transform_target,
                         num_samples=num_samples)

    @classmethod
    def from_avocado(cls, sub_set: str = 'train', transform: Optional[Callable] = None, transform_target: Optional[Callable] = None, num_samples: int = 1):
        return cls('/data/ldap/histopathologic/processed/icpr_mitosis/', sub_set, transform, transform_target, num_samples=num_samples)


class ICPR96x96Balanced(H5Dataset):
    """ 
    Data and further information can be found at TODO
    """

    def __init__(self, root: str, sub_set: str, transform: Optional[Callable] = None, transform_target: Optional[Callable] = None, num_samples: int = 1):
        assert sub_set in ['train', 'valid', 'test']

        super().__init__(data_path=Path(root) / f'{sub_set}/icpr_96_96_balanced.h5',
                         data_key='image',
                         target_path=Path(
                             root) / f'{sub_set}/icpr_96_96_balanced.h5',
                         target_key='label',
                         transform=transform,
                         transform_target=transform_target,
                         num_samples=num_samples)

    @classmethod
    def from_avocado(cls, sub_set: str = 'train', transform: Optional[Callable] = None, transform_target: Optional[Callable] = None, num_samples: int = 1):
        return cls('/data/ldap/histopathologic/processed/icpr_mitosis/', sub_set, transform, transform_target, num_samples=num_samples)

    @staticmethod
    def normalization_values():
        # Calculated on the 'train' set
        mean = [0.7802, 0.4520, 0.6357]
        std = [0.1533, 0.2005, 0.1622]
        return mean, std


class ICPR96x96Unbalanced(H5Dataset):
    """ 
    Data and further information can be found at TODO
    """

    def __init__(self, root: str, sub_set: str, transform: Optional[Callable] = None, transform_target: Optional[Callable] = None, num_samples: int = 1):
        assert sub_set in ['train', 'valid', 'test']

        super().__init__(data_path=Path(root) / f'{sub_set}/icpr_96_96_unbalanced.h5',
                         data_key='image',
                         target_path=Path(
                             root) / f'{sub_set}/icpr_96_96_unbalanced.h5',
                         target_key='label',
                         transform=transform,
                         transform_target=transform_target,
                         num_samples=num_samples)

    @classmethod
    def from_avocado(cls, sub_set: str = 'train', transform: Optional[Callable] = None, transform_target: Optional[Callable] = None, num_samples: int = 1):
        return cls('/data/ldap/histopathologic/processed/icpr_mitosis/', sub_set, transform, transform_target, num_samples=num_samples)

    @staticmethod
    def normalization_values():
        # Calculated on the 'train' set
        mean = [0.7815, 0.4431, 0.6381]
        std = [0.1396, 0.1893, 0.1483]
        return mean, std
