from pathlib import Path
from typing import Any, Callable, Optional, Tuple

import h5py
import numpy as np
from torch import Generator
from torch.utils.data import Dataset, random_split


class H5Dataset(Dataset):
    """
    Basic dataset class for handling h5 files. Do not call this class directly.
    """
    def __init__(self, data_path: str or Path, data_key: str, target_path: str or Path, target_key: str, transform: Optional[Callable] = None, transform_target: Optional[Callable] = None, num_samples: int = 1):
        """
        Args:
            data_path (str or Path): The path to the h5 files.
            data_key (str): The key of the data inside the data_path h5 file.
            target_path (str or Path): The path to the target h5 file.
            target_key (str): The key of the data inside the target h5 file.
            transform (Optional[Callable]): Transforms to apply on the data (Default: None).
            transform (Optional[Callable]): Transforms to apply on the target (Default: None).
            num_samples (int): Number of samples the __getitem__ method will return. If num_samples=1 only the element
                               of the given index is returned. If num_samples>1 a list of samples of the same class will
                               be returned.
        """
        data_path = Path(data_path)
        target_path = Path(target_path)

        self.samples = h5py.File(data_path, 'r')[data_key]
        self.targets = h5py.File(target_path, 'r')[target_key]

        self.targets = np.squeeze(self.targets)
        self.classes = list(set(self.targets))
        self.transform = transform
        self.transform_target = transform_target
        self.num_samples = num_samples

    def __getitem__(self, index: int) -> Tuple[Any, Any]:
        """
        Args:
            index (int): Index

        Returns:
            tuple: (sample, target) where target is class_index of the target class.
        """
        target = self.targets[index]
        indices = [index]
        if self.num_samples > 1:
            possible_indices = self.targets == target
            possible_indices[index] = False  # exclude original sample from random choices
            possible_indices = np.where(possible_indices)[0]
            indices.extend(np.random.choice(possible_indices, size=self.num_samples-1, replace=False))

        samples = []
        for index in indices:
            sample = self.samples[index]

            if self.transform is not None:
                sample = self.transform(sample)

            samples.append(sample)

        if self.transform_target is not None:
            target = self.transform_target(target)

        if self.num_samples == 1:
            return samples[0], target
        else:
            return (*samples, target)

    def __len__(self) -> int:
        return len(self.targets)

    def get_split(self, size: float, both_splits: bool = False, seed: int = 42):
        """ Splits the dataset randomly into two subsets.

        Args:
            size (float): Size of the first subset. Given as percentage value between 0.0 and 1.0
            both_splits (bool, optional): If set both subsets are returned. Defaults to False.
            seed (int, optional): Manual set the random seed for the generator sampling the sets. Defaults to 42.

        Returns:
            [type]: [description]
        """
        assert size > 0.0 and size < 1.0

        num_split_samples = int(len(self) * size)
        num_remaining_samples = len(self) - num_split_samples

        split_set, remaining_set = random_split(self, [num_split_samples, num_remaining_samples], generator=Generator().manual_seed(seed))
        
        if both_splits:
            return split_set, remaining_set
        else:
            return split_set
