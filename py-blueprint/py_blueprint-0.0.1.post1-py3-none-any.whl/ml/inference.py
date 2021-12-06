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

import re
import collections
import torch


class BatchList:
    """A list representing a data batch. 

    It is not defined as a Sequence type to avoid ambiguity in collate/decollate.
    """

    def __init__(self, values) -> None:
        self.values = values

    def __repr__(self) -> str:
        return 'BatchList' + repr(self.values)

    def __len__(self) -> int:
        return len(self.values)

    def __iter__(self):
        return iter(self.values)

    def __getitem__(self, index):
        return self.values[index]


class NonStackable:
    """A non-stackable object.

    A class for wraping objects that will not be stacked as tensors in `collate`.
    """

    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return f'NonStackable[{self.value}]'


_np_str_obj_array_pattern = re.compile(r'[SaUO]')

_collate_err_msg_format = (
    "collate: batch must contain tensors, numpy arrays, numbers, "
    "dicts or lists; found {}")


def collate(data):
    """A replacement of `torch.utils.data.dataloader.default_collate`.

    Try collating a data batch into combined tensors.
    """

    elem = data[0]
    elem_type = type(elem)
    if isinstance(elem, torch.Tensor):
        out = None
        if torch.utils.data.get_worker_info() is not None:
            # If we're in a background process, concatenate directly into a
            # shared memory tensor to avoid an extra copy
            numel = sum([x.numel() for x in data])
            storage = elem.storage()._new_shared(numel)
            out = elem.new(storage)
        return torch.stack(data, 0, out=out)
    elif elem_type.__module__ == 'numpy' and elem_type.__name__ != 'str_' \
            and elem_type.__name__ != 'string_':
        elem = data[0]
        if elem_type.__name__ == 'ndarray':
            # array of string classes and object
            if _np_str_obj_array_pattern.search(elem.dtype.str) is not None:
                raise TypeError(
                    _collate_err_msg_format.format(elem.dtype))

            return collate([torch.as_tensor(b) for b in data])
        elif elem.shape == ():  # scalars
            return torch.as_tensor(data)
    elif isinstance(elem, float):
        return torch.tensor(data, dtype=torch.float64)
    elif isinstance(elem, int):
        return torch.tensor(data)
    elif isinstance(elem, (str, bytes, NonStackable)):
        return BatchList(data)
    elif isinstance(elem, collections.abc.Mapping):
        return {key: collate([d[key] for d in data]) for key in elem}
    elif isinstance(elem, tuple) and hasattr(elem, '_fields'):  # namedtuple
        return elem_type(*(collate(samples) for samples in zip(*data)))
    elif isinstance(elem, collections.abc.Sequence):
        transposed = zip(*data)
        return [collate(samples) for samples in transposed]


def _simplify_np_array(npa):
    if npa.shape == ():
        return npa.item()
    return npa


def decollate(data) -> BatchList:
    """The inverse process of `collate`.

    Try spliting the batched data back as numpy lists.
    """

    if isinstance(data, torch.Tensor):
        return BatchList([_simplify_np_array(e.detach().cpu().numpy())
                          for e in data.unbind(dim=0)])
    elif isinstance(data, BatchList):
        return data
    elif isinstance(data, (str, bytes, int, float, NonStackable)):
        raise TypeError(
            f'trying to decollate a non-batched type: {type(data)}')
    elif isinstance(data, collections.abc.Sequence):
        return BatchList(zip(*[decollate(e) for e in data]))
    elif isinstance(data, collections.abc.Mapping):
        data_dc = [(key, decollate(data[key])) for key in data]
        return BatchList([{key: val[ind] for key, val in data_dc}
                          for ind in range(len(data_dc[0][1]))])
