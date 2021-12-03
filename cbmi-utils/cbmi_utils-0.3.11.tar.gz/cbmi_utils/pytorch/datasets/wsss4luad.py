from pathlib import Path
from typing import Callable, Optional

from .h5_dataset import H5Dataset


class WSSS4LUAD96x96(H5Dataset):
    """
    Data and further information can be found at https://wsss4luad.grand-challenge.org/
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
        
        self.classes = ['tumor', 'stroma', 'normal']

    @classmethod
    def from_avocado(cls, sub_set: str = 'train', transform: Optional[Callable] = None, transform_target: Optional[Callable] = None, num_samples: int = 1):
        return cls('/data/ldap/histopathologic/processed_read_only/WSSS4LUAD_96', sub_set, transform, transform_target, num_samples=num_samples)
