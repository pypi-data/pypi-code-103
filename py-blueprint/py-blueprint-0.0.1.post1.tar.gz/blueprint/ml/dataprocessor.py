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

import os
import shutil
from typing import Optional, Tuple, List, Union

import numpy as np
import random
import math
import torch
from torch.utils.data import (
    DataLoader, Sampler, DistributedSampler, RandomSampler, SequentialSampler)
from torch import distributed as dist

from .dataset import (
    Dataset, DatasetRepeatingConstantValue, ConcatDataset, Subset)
from .augmenters import augment_each
from .inference import collate, decollate
from .storage import Frozen
from .augmenters import AugLike


from .util import barrier
from .task import Task, ForwardFlags

from ..context import Context


__all__ = ['DataProcessor', 'DataSource']


class _WorkerInitFunction:
    def __init__(self, rank) -> None:
        self.rank = rank

    def __call__(self, worker_id):
        seed = worker_id * 1000 + self.rank
        torch.manual_seed(seed)
        random.seed(seed+100)
        np.random.seed(seed+200)


def _get_data_loader_and_sampler(
        dataset: Dataset, batch_size: int,
        randomize: bool = False, num_workers: int = 0,
        validity_tag: str = 'valid') -> Tuple[DataLoader, Sampler]:
    """Get the DataLoader and Sampler from a dataset.
    """
    if dist.is_initialized():
        world_size = dist.get_world_size()
    else:
        world_size = 1

    dataset = dataset.make_evenly_divisible(
        world_size * batch_size, validity_tag=validity_tag)
    assert len(dataset) % (world_size * batch_size) == 0

    if dist.is_initialized():
        sampler = DistributedSampler(
            dataset, shuffle=randomize, drop_last=False)
        rank = dist.get_rank()
    else:
        if randomize:
            sampler = RandomSampler(dataset)
        else:
            sampler = SequentialSampler(dataset)
        rank = 0

    data_loader = DataLoader(
        dataset, batch_size=batch_size, sampler=sampler,
        collate_fn=collate, drop_last=False,
        num_workers=num_workers,
        pin_memory=True, worker_init_fn=_WorkerInitFunction(rank))
    return data_loader, sampler


def _load_frozen_dataset(filepath, copy2local=True, local_filepath=None,
                         subset_ids=None):
    if copy2local:
        if local_filepath is None:
            local_filepath = os.path.basename(filepath)

        # dist
        if not dist.is_initialized():
            if not os.path.exists(local_filepath):
                print(
                    f'Copying {filepath} to local directory {local_filepath}')
                shutil.copy(filepath, local_filepath)
        else:
            if torch.cuda.current_device() == 0:
                if not os.path.exists(local_filepath):
                    print(
                        f'Copying {filepath} to local directory {local_filepath}')
                    shutil.copy(filepath, local_filepath)
            barrier()
        filepath = local_filepath
    dataset = Frozen(filepath)
    if subset_ids is not None:
        dataset = Subset(dataset, subset_ids)
    return dataset


class DataSource:
    """Data source representation.

    Args:
        data_path (Union[str, List[str]]): A frozen zip path, or a list of paths.
        random_ratio (Optional[float]): When random_ratio < 1.0, a subset of 
            data with random_ratio would be randomly sampled from the original dataset. 
            However, the data size is unchanged through random repeating.
        subset_ids (Optional[List[int]]): Subset data indices.
        augmentations (AugLike): Data transforms before feeding into network.
        post_augmentations (AugLike): Data transforms appended to the network outputs.

    """

    def __init__(self, data_path: Union[str, List[str]],
                 random_ratio: Optional[float] = None,
                 random_subsample_seed: int = 123,
                 augmentations: AugLike = None,  post_augmentations: AugLike = None,
                 subset_ids: Optional[List[int]] = None,
                 _ctx: Optional[Context] = None):
        if isinstance(data_path, str):
            data_path = [data_path]
        self.data_path = data_path

        dataset = ConcatDataset([
            _load_frozen_dataset(os.path.join(
                _ctx.blob_root, p), copy2local=_ctx.copy2local)
            for p in self.data_path])

        if random_ratio is not None:
            rnd = random.Random(random_subsample_seed)
            orig_len = len(dataset)
            selected_ids = list(range(orig_len))
            rnd.shuffle(selected_ids)
            del selected_ids[int(orig_len*random_ratio):]
            assert len(set(selected_ids)) == int(orig_len*random_ratio)
            # repeat the selected ids to orig_len
            selected_ids = selected_ids * math.ceil(orig_len/len(selected_ids))
            del selected_ids[orig_len:]
            assert len(selected_ids) == orig_len
            assert len(set(selected_ids)) == int(orig_len*random_ratio)
            dataset = Subset(dataset, selected_ids)

        if subset_ids is not None:
            dataset = Subset(dataset, subset_ids)

        self.dataset = dataset
        self.augmentations = augmentations
        self.dataset_augmented = self.dataset.augment(self.augmentations)
        self.post_augmentations = post_augmentations


class DataProcessor:
    """Data processors.

    DataProcessor processes data following the pipleline as below:
    ```
        Data loaded from data_path 
            -> augmentations 
            -> collate as input data batches in DataLoader [A]
            -> task_module generates output data batches
            -> decollate data batches as individual data samples
            -> post augmentations
            -> final results [B]
    ```

    Use `iterate_input` to iterate the data batches in [A], 
    use `iterate_final_result` to iterate the final results in [B].

    """

    def __init__(self, data_src: DataSource, batch_size: int,
                 randomize: bool, num_workers: int = 2,
                 validity_tag: str = 'valid',
                 repeats_constant: bool = False) -> None:
        self.data_src = data_src
        self.validity_tag = validity_tag

        dataset_augmented = self.data_src.dataset_augmented
        if repeats_constant:
            dataset_augmented = DatasetRepeatingConstantValue(
                dataset_augmented[0], len(dataset_augmented))

        self.data_loader, self.sampler = _get_data_loader_and_sampler(
            dataset_augmented, batch_size=batch_size,
            randomize=randomize, num_workers=num_workers, validity_tag=validity_tag)

    def num_steps_of_epoch(self, epoch_idx: int = 0) -> int:
        if self.data_loader is None:
            self.load()
        if hasattr(self.sampler, 'set_epoch'):
            self.sampler.set_epoch(epoch_idx)
        return len(self.data_loader)

    def iterate_input(self, epoch_idx: int = 0):
        """Iterate the batched data input to nn.Modules. 

        By default most data will be torch.Tensor.
        """
        if self.data_loader is None:
            self.load()
        if hasattr(self.sampler, 'set_epoch'):
            self.sampler.set_epoch(epoch_idx)
        return iter(self.data_loader)

    def iterate_final_result(self, task_module: Task, epoch_idx: int = 0):
        """Iterate the final non-batched data after post_augmentation.

        By default most data will be np.ndarray.
        """
        with torch.no_grad():
            for batch_data in self.iterate_input(epoch_idx):
                _, _, batch_result, _ = task_module(
                    batch_data, ForwardFlags(with_losses=False, with_outputs=True,
                                             with_images=False))
                full_batch = {**batch_data, **batch_result}
                for single_result in augment_each(decollate(full_batch).values,
                                                  self.data_src.post_augmentations):
                    is_valid_data = single_result.get(self.validity_tag, True)
                    if is_valid_data:
                        yield single_result
