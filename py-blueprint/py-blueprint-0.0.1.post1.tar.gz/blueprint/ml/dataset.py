# MIT License

# Copyright (c) 2021 Hao Yang (yanghao.alexis@foxmail.com)

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import numpy as np
import torch
import torch.utils
import torch.utils.data
import bisect
from enum import Enum


class Split(Enum):
    ALL = 0
    TRAIN = 1
    VAL = 2
    TEST = 3
    REFINED_TEST = 4
    TOY = 5


ALL = Split.ALL
TRAIN = Split.TRAIN
VAL = Split.VAL
TEST = Split.TEST
REFINED_TEST = Split.REFINED_TEST
TOY = Split.TOY


class Dataset(torch.utils.data.Dataset):
    """The augmentable dataset. All augmentable dataset should derive this class.

    Comparing to torch.utils.data.Dataset, this class should further implement the `sample_name` method.
    """

    def augment(self, aug):
        from .augmenters import augment
        return augment(self, aug)

    def sample_name(self, index) -> str:
        """The name of this sample.
        """
        raise NotImplementedError()

    def extra_data(self) -> dict:
        return dict()

    def subset(self, indices):
        return Subset(self, indices)

    def attach_index_as_tag(self):
        return _DatasetWithIndexAsTag(self)

    def attach_sample_name_as_tag(self):
        return _DatasetWithSampleNameAsTag(self)

    def validate_sample_names(self, valid_sample_names):
        return _DatasetWithValidSampleNames(self, valid_sample_names)

    def invalidate_sample_names(self, invalid_sample_names):
        return _DatasetWithInvalidSampleNames(self, invalid_sample_names)

    def make_evenly_divisible(self, divisor: int, validity_tag: str = 'valid'):
        return _DatasetEvenlyDivisible(self, divisor, validity_tag)

    def collect_as_dict(self, tag_to_collect, with_prog=False):
        collected = dict()
        if with_prog:
            from tqdm.auto import tqdm
            p = tqdm(self)
        else:
            p = self
        for i, d in enumerate(p):
            collected[self.sample_name(i)] = d[tag_to_collect]
        return collected


class Subset(Dataset):
    """Subset of a dataset at specified indices.

    Args:
        dataset (Dataset): The whole Dataset
        indices (list): Indices in the whole set selected for subset
    """

    def __init__(self, dataset, indices):
        self.dataset = dataset
        self.indices = indices

    def __getitem__(self, idx):
        return self.dataset[self.indices[idx]]

    def sample_name(self, idx):
        return self.dataset.sample_name(self.indices[idx])

    def __len__(self):
        return len(self.indices)

    def extra_data(self) -> dict:
        return self.dataset.extra_data()


class ConcatDataset(Dataset):
    """Dataset as a concatenation of multiple datasets.

    This class is useful to assemble different existing datasets.

    Args:
        datasets: List of datasets to be concatenated
    """

    @staticmethod
    def cumsum(sequence):
        r, s = [], 0
        for e in sequence:
            l = len(e)
            r.append(l + s)
            s += l
        return r

    def __init__(self, datasets):
        assert len(datasets) > 0, 'datasets should not be an empty iterable'
        self.datasets = list(datasets)
        self.cumulative_sizes = self.cumsum(self.datasets)

    def __len__(self):
        return self.cumulative_sizes[-1]

    def _get_dataset_sample_inds(self, idx):
        if idx < 0:
            if -idx > len(self):
                raise ValueError(
                    "absolute value of index should not exceed dataset length")
            idx = len(self) + idx
        dataset_idx = bisect.bisect_right(self.cumulative_sizes, idx)
        if dataset_idx == 0:
            sample_idx = idx
        else:
            sample_idx = idx - self.cumulative_sizes[dataset_idx - 1]
        return dataset_idx, sample_idx

    def __getitem__(self, idx):
        dataset_idx, sample_idx = self._get_dataset_sample_inds(idx)
        return self.datasets[dataset_idx][sample_idx]

    def sample_name(self, idx):
        dataset_idx, sample_idx = self._get_dataset_sample_inds(idx)
        return self.datasets[dataset_idx].sample_name(sample_idx)

    def extra_data(self) -> dict:
        result = dict()
        for ds in self.datasets:
            result.update(ds.extra_data())
        return result


class _DatasetWithIndexAsTag(Dataset):
    def __init__(self, orig_dataset, tag='index'):
        self.orig_dataset = orig_dataset
        self.tag = tag

    def sample_name(self, index):
        return self.orig_dataset.sample_name(index)

    def __len__(self):
        return len(self.orig_dataset)

    def __getitem__(self, index):
        return {self.tag: index, **self.orig_dataset[index]}

    def extra_data(self) -> dict:
        return self.orig_dataset.extra_data()


class _DatasetWithSampleNameAsTag(Dataset):
    def __init__(self, orig_dataset, tag='sample_name'):
        self.orig_dataset = orig_dataset
        self.tag = tag

    def sample_name(self, index):
        return self.orig_dataset.sample_name(index)

    def __len__(self):
        return len(self.orig_dataset)

    def __getitem__(self, index):
        return {self.tag: self.orig_dataset.sample_name(index),
                **self.orig_dataset[index]}

    def extra_data(self) -> dict:
        return self.orig_dataset.extra_data()


class _DatasetWithValidSampleNames(Dataset):
    def __init__(self, orig_dataset, valid_sample_names):
        self.orig_dataset = orig_dataset
        self.valid_inds = []
        for i in range(len(orig_dataset)):
            if orig_dataset.sample_name(i) in valid_sample_names:
                self.valid_inds.append(i)

    def sample_name(self, index):
        return self.orig_dataset.sample_name(self.valid_inds[index])

    def __len__(self):
        return len(self.valid_inds)

    def __getitem__(self, index):
        return self.orig_dataset[self.valid_inds[index]]

    def extra_data(self) -> dict:
        return self.orig_dataset.extra_data()


class _DatasetWithInvalidSampleNames(Dataset):
    def __init__(self, orig_dataset, invalid_sample_names):
        self.orig_dataset = orig_dataset
        self.valid_inds = []
        for i in range(len(orig_dataset)):
            if orig_dataset.sample_name(i) not in invalid_sample_names:
                self.valid_inds.append(i)

    def sample_name(self, index):
        return self.orig_dataset.sample_name(self.valid_inds[index])

    def __len__(self):
        return len(self.valid_inds)

    def __getitem__(self, index):
        return self.orig_dataset[self.valid_inds[index]]

    def extra_data(self) -> dict:
        return self.orig_dataset.extra_data()


class _DatasetEvenlyDivisible(Dataset):
    def __init__(self, dataset: Dataset, divisor: int, validity_tag: str = 'valid'):
        self.dataset = dataset
        self.divisible_len = len(self.dataset)
        if self.divisible_len % divisor > 0:
            self.divisible_len += (divisor-self.divisible_len % divisor)
        assert self.divisible_len % divisor == 0
        assert self.divisible_len >= len(self.dataset)
        self.validity_tag = validity_tag

    def __len__(self):
        return self.divisible_len

    def __getitem__(self, index):
        if index < 0:
            index += self.divisible_len
        data = self.dataset[index % len(self.dataset)]
        return {self.validity_tag: (index < len(self.dataset)), **data}

    def sample_name(self, index) -> str:
        if index < 0:
            index += self.divisible_len
        return self.dataset.sample_name(index % len(self.dataset))

    def extra_data(self) -> dict:
        return self.dataset.extra_data()


class DatasetRepeatingConstantValue(Dataset):
    def __init__(self, value, length: int):
        self.value = value
        self.length = length

    def __len__(self):
        return self.length

    def __getitem__(self, index):
        return self.value

    def sample_name(self, index) -> str:
        return f'constant_{index}'
