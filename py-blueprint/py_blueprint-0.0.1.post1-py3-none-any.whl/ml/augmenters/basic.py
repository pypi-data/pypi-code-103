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

import collections
from typing import List, Optional, Tuple, Dict, Set, Mapping, Union, Any, Callable

import numpy as np
from copy import deepcopy

from ..util import record_time
from ..inference import NonStackable
from ..dataset import Dataset


class AugBase(object):
    r"""Base class for all augmenters
    """

    def process(self, data: Any):
        raise NotImplementedError()


AugLike = Union[AugBase, list, Callable[..., Any], None]


class AugmentedDataset(Dataset):
    """The augmented dataset.

    Args:
        dataset: The original dataset before augmentation
        aug: The augmenter
    """

    def __init__(self, dataset: Dataset, aug: AugBase):
        self.dataset = dataset
        self.aug = aug

    def __len__(self):
        return len(self.dataset)

    def sample_name(self, index):
        return self.dataset.sample_name(index)

    def __getitem__(self, index):
        return self.aug.process(self.dataset[index])

    def extra_data(self) -> dict:
        return self.dataset.extra_data()


def _wrap_aug(aug: AugLike) -> AugBase:
    if isinstance(aug, list):
        aug = Sequential(aug)
    elif callable(aug):
        aug = Lambda(aug)
    elif aug is None:
        aug = DoNothing()
    assert isinstance(aug, AugBase)
    return aug


def augment(dataset: Dataset, aug: AugLike):
    r"""Augment a dataset with given augmenter

    Args:
        dataset: The original dataset
        aug: The augmenter
    """
    return AugmentedDataset(dataset, _wrap_aug(aug))


def augment_each(data_seq: collections.abc.Sequence, aug: AugLike):
    r"""Augment a given data sequence with given augmenter

    Args:
        data_seq: The input data sequence
        aug: The augmenter
    """
    aug = _wrap_aug(aug)
    for data in data_seq:
        yield aug.process(data)


class DoNothing(AugBase):
    r"""An augmenter that does nothing
    """

    def process(self, data):
        return data


class Sequential(AugBase):
    r"""A sequence of augmenters that applies in a one-by-one style
    """

    def __init__(self, sub_augs: List[AugLike]):
        self.sub_augs = [_wrap_aug(aug) for aug in sub_augs]

    def process(self, data):
        for aug in self.sub_augs:
            data = aug.process(data)
        return data


class Benchmark(AugBase):
    """An augmenter to measure time cost

    Args:
        name (str): A name for printing
        sub_aug: The augmenter whose time to measure
    """

    def __init__(self, name: str, sub_aug: AugLike):
        self.name = name
        self.sub_aug = _wrap_aug(sub_aug)

    def process(self, data):
        with record_time(self.name):
            ret = self.sub_aug.process(data)
        return ret


class Lambda(AugBase):
    r"""An augmenter that warps a functor within
    """

    def __init__(self, func):
        self.func = func

    def process(self, data):
        if isinstance(data, tuple):
            return self.func(*data)
        else:
            return self.func(data)


class With(AugBase):
    """An augmenter that wraps another augmenter with both input and output tag names
    """

    def __init__(self,
                 input_tags: Union[str, List[str], None] = None,
                 output_tags: Union[str, List[str], None] = None,
                 aug: AugLike = None,
                 tags_str: Optional[str] = None):

        if tags_str is not None:
            if not (input_tags is None and output_tags is None):
                raise RuntimeError(
                    'When tag_str is given, input_tags '
                    'and output_tags should both be None.')
            input_tags_str, output_tags_str = tags_str.split('->')

            def _interpret_tags_str(tags_str):
                tags = [s.strip() for s in tags_str.split(',')]
                if len(tags) == 1:
                    tags = tags[0]
                return tags
            input_tags = _interpret_tags_str(input_tags_str)
            output_tags = _interpret_tags_str(output_tags_str)

        self.input_tags = input_tags
        self.output_tags = output_tags

        self.aug = _wrap_aug(aug)

    @staticmethod
    def _get_value(data, tag):
        if isinstance(tag, str):
            return data[tag]
        return tag

    def process(self, data):
        if not isinstance(data, dict):
            raise RuntimeError(
                f'Please input dict data into the `With` augmenter.')

        if isinstance(self.input_tags, tuple):
            result = self.aug.process(
                tuple([__class__._get_value(data, tag)
                       for tag in self.input_tags]))
        elif isinstance(self.input_tags, list):
            result = self.aug.process([
                __class__._get_value(data, tag)
                for tag in self.input_tags])
        else:
            result = self.aug.process(
                __class__._get_value(data, self.input_tags))

        if isinstance(self.output_tags, str):
            return {**data, self.output_tags: result}
        elif isinstance(self.output_tags, (tuple, list)):
            assert isinstance(result, (tuple, list))
            assert len(self.output_tags) == len(result)
            result = {tag: re for tag, re in zip(self.output_tags, result)}
            return {**data, **result}
        else:
            raise RuntimeError(
                f'Unsupported output_tags type: {type(self.output_tags)}.')


class Rename(AugBase):
    """An augmenter that renames tags
    """

    def __init__(self, tag_names_mapping: Mapping[str, str]):
        self.tag_names_mapping = tag_names_mapping

    def process(self, data):
        out_data = dict()
        for tag_name, d in data.items():
            tag_name = self.tag_names_mapping.get(tag_name, tag_name)
            out_data[tag_name] = d
        return out_data


class DeepCopy(AugBase):
    """An augmenter that deepcopies tags
    """

    def __init__(self, tag_names_mapping: Mapping[str, str]):
        self.tag_names_mapping = tag_names_mapping

    def process(self, data):
        out_data = deepcopy(data)
        for tag_name, d in data.items():
            if tag_name in self.tag_names_mapping:
                out_data[self.tag_names_mapping[tag_name]] = d
        return out_data


class If(AugBase):
    """ condition:bool, input_value -> output_value
    """

    def __init__(self, then_branch: AugLike, else_branch: AugLike = None):
        self.then_branch = _wrap_aug(then_branch)
        self.else_branch = _wrap_aug(else_branch)

    def process(self, data):
        assert isinstance(data, tuple)
        cond, input_value = data
        assert isinstance(cond, bool)
        if cond:
            return self.then_branch.process(input_value)
        else:
            return self.else_branch.process(input_value)


class IfExist(AugBase):
    """ execute then_aug only if tags are all available.
    """

    def __init__(self, tags: Union[str, Set[str]], then_branch: AugLike, else_branch: AugLike = None):
        if isinstance(tags, str):
            tags = {tags}
        self.tags = set(tags)
        self.then_branch = _wrap_aug(then_branch)
        self.else_branch = _wrap_aug(else_branch)

    def process(self, data: Dict[str, Any]):
        if self.tags <= data.keys():
            return self.then_branch.process(data)
        else:
            return self.else_branch.process(data)


class AttachConstData(AugBase):
    r"""An augmenter that attaches a constant as new tag

    Example:

        >>> # you can attach any data using this code:
        >>> ds = ds.augment(AttachConstData('new_tag_name', const_data))

    """

    def __init__(self, tag_name: str, const_data: Any):
        self.tag_name = tag_name
        self.const_data = const_data

    def process(self, data):
        if self.tag_name in data:
            raise RuntimeWarning(
                f'existing tags already include the "{self.tag_name}", '
                f'whose data will be overwritten by AttachConstData')
        return {self.tag_name: self.const_data, **data}


class AttachListData(AugBase):
    r"""An augmenter that attaches a list as new tag

    Example:

        >>> # if list_data = [new_data1, new_data2, ...]
        >>> # then you can attach these data using this code:
        >>> ds = ds.augment(AttachListData('new_tag_name', list_data))

    """

    def __init__(self, tag_name: str, list_data: List[Any]):
        self.tag_name = tag_name
        self.list_data = list_data

    def process(self, data):
        assert isinstance(data, dict)
        if 'index' not in data:
            raise RuntimeError(
                'existing tags do not include "index", '
                'call .attach_index_as_tag() before using AttachListData')
        if self.tag_name in data:
            raise RuntimeWarning(
                f'existing tags already include the "{self.tag_name}", '
                f'whose data will be overwritten by AttachListData')
        return {self.tag_name: self.list_data[data['index']], **data}


class AttachDictData(AugBase):
    r"""An augmenter that attaches a dict as new tag

    Example:

        >>> # if dict_data = {sample_name1:new_data1, sample_name2:new_data2, ...}
        >>> # then you can attach these data using this code:
        >>> ds = ds.augment(AttachDictData('new_tag_name', dict_data))

    """

    def __init__(self, tag_name: str, dict_data: Dict[str, Any]):
        self.tag_name = tag_name
        self.dict_data = dict_data

    def process(self, data):
        assert isinstance(data, dict)
        if 'sample_name' not in data:
            raise RuntimeError(
                'existing tags do not include "sample_name", '
                'call .attach_sample_name_as_tag() before using AttachDictData')
        if self.tag_name in data:
            raise RuntimeWarning(
                f'existing tags already include the "{self.tag_name}", '
                f'whose data will be overwritten by AttachDictData')
        return {self.tag_name: self.dict_data[data['sample_name']], **data}


class Filter(AugBase):
    """ dict -> dict
    """

    def __init__(self, tags, strict=False):
        self.tags = tags
        self.strict = strict

    def process(self, data):
        assert isinstance(data, dict)
        if self.strict:
            return {name: data[name] for name in self.tags}
        else:
            return {name: data[name] for name in self.tags if name in data}


class Maybe(AugBase):
    """ randomly perform the augmenter given a probability """

    def __init__(self, prob: float, then_branch: AugLike, else_branch: AugLike = None):
        self.prob = prob
        self.then_branch = _wrap_aug(then_branch)
        self.else_branch = _wrap_aug(else_branch)

    def process(self, data):
        selected = (np.random.uniform() <= self.prob)
        if selected:
            data = self.then_branch.process(data)
        else:
            data = self.else_branch.process(data)
        return data


class RandomSwitch(AugBase):
    """ randomly pick one of the multiple branches with given probabilities """

    def __init__(self, prob_branches: List[Tuple[float, AugLike]]):
        self.probs = [branch[0] for branch in prob_branches]
        self.branches = [_wrap_aug(branch[1]) for branch in prob_branches]

    def process(self, data):
        selected = np.random.choice(len(self.probs), p=self.probs)
        return self.branches[selected].process(data)


class RandomPick(AugBase):
    """ randomly pick an element from a container 

        a list -> an element
    """

    def process(self, data):
        return np.random.choice(data)


class MakeNonStackable(AugBase):
    """ make this data non-stackable in collate """

    def process(self, data):
        if isinstance(data, NonStackable):
            return data
        else:
            return NonStackable(data)


class UnwrapNonStackable(AugBase):
    """ get the original data from the non-stackable wrapper """

    def process(self, data):
        if isinstance(data, NonStackable):
            return data.value
        else:
            return data
