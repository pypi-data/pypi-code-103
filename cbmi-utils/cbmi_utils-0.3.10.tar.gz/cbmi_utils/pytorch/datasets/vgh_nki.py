from pathlib import Path
from typing import Callable, Optional

from .h5_dataset import H5Dataset


class VGHNKI(H5Dataset):
    """
    Data and further information can be found at https://github.com/AdalbertoCq/Pathology-GAN#datasets
    """

    def __init__(self, root: str, sub_set: str, transform: Optional[Callable] = None, transform_target: Optional[Callable] = None, num_samples: int = 1):
        assert sub_set in ['train', 'valid', 'test']  # TODO valid does not exist, probably need to create one from train.h5

        super().__init__(data_path=Path(root) / f'hdf5_vgh_nki_he_{sub_set}.h5',
                         data_key=f'{sub_set}_img',
                         target_path=Path(
                             root) / f'hdf5_vgh_nki_he_{sub_set}.h5',
                         target_key=f'{sub_set}_labels',
                         transform=transform,
                         transform_target=transform_target,
                         num_samples=num_samples)

    @classmethod
    def from_avocado(cls, sub_set: str = 'train', transform: Optional[Callable] = None, transform_target: Optional[Callable] = None, num_samples: int = 1):
        return cls('/data/ldap/histopathologic/original_read_only/vgh_nki/vgh_nki/he/patches_h224_w224', sub_set, transform, transform_target, num_samples=num_samples)
