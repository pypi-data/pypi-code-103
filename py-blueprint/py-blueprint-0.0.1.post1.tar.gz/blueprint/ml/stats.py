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

import operator
from typing import Mapping, MutableMapping, Any

import torch
import torch.distributed as dist


def _reduce_to_dict(d: MutableMapping[str, Any], name: str, val: Any,
                    reduce_op: 'dist.ReduceOp'):

    if reduce_op == dist.ReduceOp.SUM:
        reduce_op = operator.add
    elif reduce_op == dist.ReduceOp.PRODUCT:
        reduce_op = operator.mul
    elif reduce_op == dist.ReduceOp.MIN:
        reduce_op = min
    elif reduce_op == dist.ReduceOp.MAX:
        reduce_op = max

    if isinstance(val, torch.Tensor):
        if reduce_op == min:
            reduce_op = torch.min
        elif reduce_op == max:
            reduce_op = torch.max
    if name in d:
        d[name] = reduce_op(d[name], val)
    else:
        d[name] = val


def _reduce_all_distributed(d: Mapping[str, torch.Tensor],
                            reduce_op: 'dist.ReduceOp'):
    reduced = dict()
    for name, val in d.items():
        reduced_val = torch.tensor(val)
        dist.all_reduce(reduced_val, op=reduce_op)
        reduced[name] = reduced_val
    return reduced


def _simplify_tensor(t: torch.Tensor):
    if t.numel() == 1:
        return t.item()
    return t


class StatSummary:
    """Summary of all statistics.
    """

    def __init__(self, device=torch.device('cpu')):
        self.sums = dict()
        self.sum_sqs = dict()
        self.mins = dict()
        self.maxs = dict()
        self.count = 0
        self.device = device

    def update(self, batch_stat: Mapping[str, torch.Tensor]):
        """Update statistics from one batch.
        """

        batch_size = None
        for name, batch in batch_stat.items():
            batch = batch.detach().to(self.device)
            if batch.is_floating_point():
                batch = batch.float()

            _reduce_to_dict(self.sums, name, batch.sum([0]), dist.ReduceOp.SUM)
            _reduce_to_dict(self.sum_sqs, name, batch.pow(
                2).sum([0]), dist.ReduceOp.SUM)

            batch_min_v, _ = batch.min(0)
            _reduce_to_dict(self.mins, name, batch_min_v, dist.ReduceOp.MIN)

            batch_max_v, _ = batch.max(0)
            _reduce_to_dict(self.maxs, name, batch_max_v, dist.ReduceOp.MAX)

            if batch_size is not None:
                if batch_size != batch.size(0):
                    raise RuntimeError(
                        f'The first dimension of {name} ({batch.size(0)}) does not '
                        f'match the previously recorded batch size ({batch_size})')
            else:
                batch_size = batch.size(0)
        if batch_size is not None:
            self.count += batch_size

    def gather(self):
        """Gather statistics from all other threads.
        """

        self.sums = _reduce_all_distributed(self.sums, dist.ReduceOp.SUM)
        self.sum_sqs = _reduce_all_distributed(self.sum_sqs, dist.ReduceOp.SUM)
        self.mins = _reduce_all_distributed(self.mins, dist.ReduceOp.MIN)
        self.maxs = _reduce_all_distributed(self.maxs, dist.ReduceOp.MAX)
        count = torch.tensor(self.count)
        dist.all_reduce(count, op=dist.ReduceOp.SUM)
        self.count = count.item()

    def get_averages(self) -> Mapping[str, Any]:
        return {name: _simplify_tensor(s/self.count) for name, s in self.sums.items()}

    def get_stddevs(self) -> Mapping[str, Any]:
        avgs = self.get_averages()
        avg_sqs = {name: _simplify_tensor(s/self.count)
                   for name, s in self.sum_sqs.items()}
        stddevs = dict()
        for name, _ in self.sums.items():
            stddevs[name] = (avg_sqs[name] - avgs[name] ** 2) ** 0.5
        return stddevs
