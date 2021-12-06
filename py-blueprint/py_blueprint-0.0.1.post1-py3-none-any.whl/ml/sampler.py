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

from typing import Optional, Dict, List, Union

import torch
import torch.distributed as dist
from torch.utils.data import DistributedSampler

from .dataset import Dataset, ConcatDataset


class DistributedRandomMixSampler(torch.utils.data.Sampler):
    """Distributed random mix sampler.

    Args:
        dataset (Dataset): a dataset concatenating multiple datasets.
        num_samples_each_thread (int): number of samples to iterate for each thread.
        seed (int): Seed for a local random sampler.
    """

    def __init__(self, dataset: Dataset,
                 num_samples_each_thread: Optional[int] = None,
                 num_replicas: Optional[int] = None,
                 rank: Optional[int] = None, seed: int = 0):
        if num_replicas is None:
            if not dist.is_available():
                raise RuntimeError(
                    "Requires distributed package to be available")
            num_replicas = dist.get_world_size()
        if rank is None:
            if not dist.is_available():
                raise RuntimeError(
                    "Requires distributed package to be available")
            rank = dist.get_rank()
        if rank >= num_replicas or rank < 0:
            raise ValueError(
                "Invalid rank {}, rank should be in the interval"
                " [0, {}]".format(rank, num_replicas - 1))

        if not isinstance(dataset, ConcatDataset):
            dataset = ConcatDataset([dataset])

        self.dataset = dataset
        self.num_replicas = num_replicas
        self.rank = rank
        self.epoch = 0

        if num_samples_each_thread is None:
            num_samples_each_thread = (
                min([len(ds) for ds in self.dataset.datasets]) +
                self.num_replicas - 1) // self.num_replicas

        self.num_samples_each_thread = num_samples_each_thread
        self.seed = seed

    def __iter__(self):
        indices_table = []
        acc_len = 0

        # deterministically shuffle based on epoch and seed
        g = torch.Generator()
        g.manual_seed(self.seed + self.epoch)
        for ds in self.dataset.datasets:
            indices_table.append(
                (torch.randperm(len(ds), generator=g)+acc_len))
            acc_len += len(ds)

        # subsample
        ds_id = self.rank % len(indices_table)
        index_ids = [0] * len(indices_table)
        for _ in range(self.num_samples_each_thread):
            index_id = index_ids[ds_id]
            sample_id = indices_table[ds_id][(
                index_id * self.num_replicas + self.rank) % len(indices_table[ds_id])]

            index_ids[ds_id] += 1
            ds_id = (ds_id + 1) % len(indices_table)
            yield sample_id

    def __len__(self) -> int:
        return self.num_samples_each_thread

    def set_epoch(self, epoch: int) -> None:
        self.epoch = epoch


UnifiedDistributedSampler = Union[DistributedSampler,
                                  DistributedRandomMixSampler]
