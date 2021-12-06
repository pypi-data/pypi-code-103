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
import random
import numpy as np
from copy import deepcopy
import torch
import torch.distributed as dist

from packaging import version

from ..builder import Builder


def _single_thread_run(gpu_rank, num_gpus, distributed_run: 'DistributedGPURun'):
    rank = distributed_run.node_rank * num_gpus + gpu_rank
    world_size = num_gpus * distributed_run.num_nodes

    if distributed_run.num_nodes == 1:
        init_method = 'tcp://localhost:10315'
    elif 'AZ_BATCHAI_PYTORCH_INIT_METHOD' in os.environ:
        init_method = os.environ['AZ_BATCHAI_PYTORCH_INIT_METHOD']
    elif 'MASTER_ADDR' in os.environ and 'MASTER_PORT' in os.environ:
        init_method = "tcp://%s:%s" % (
            os.environ['MASTER_ADDR'], os.environ['MASTER_PORT'])
    else:
        raise RuntimeError('Failed to create the init_method')

    dist.init_process_group(
        backend='nccl',
        init_method=init_method,
        rank=rank, world_size=world_size)

    print(f'DistributedGPURun: init_process_group: {rank}/{world_size}')

    torch.cuda.set_device(gpu_rank)
    seed = distributed_run.seed0 + rank
    torch.manual_seed(seed)
    random.seed(seed+100)
    np.random.seed(seed+200)

    # update the context for each thread
    builder: Builder = deepcopy(distributed_run.builder_snapshot)

    # the local_run is instantiated on each thread with renewed context
    local_run = builder.parse_cfg_object(distributed_run.local_run)

    local_run()

    # add a barrier to avoid `broken pipe` error
    # see https://github.com/pytorch/pytorch/issues/40633#issuecomment-651354635
    if version.parse(torch.__version__) >= version.parse('1.8.0'):
        dist.barrier(device_ids=[gpu_rank])
    else:
        dist.barrier()

    dist.destroy_process_group()


class DistributedGPURun:
    """Run another runnable object on distributed GPU nodes. 

    Supported by PyTorch utility.

    Args:
        local_run: The wrapped local run. 
            It runs on each local thread in each node.
        seed0: The intial seed for reproducibility.
    """

    @staticmethod
    def __parse_inputs__(local_run):
        return local_run

    def __init__(self, local_run, seed0: int = 123) -> None:
        if 'NODE_COUNT' in os.environ:
            self.num_nodes = int(os.environ['NODE_COUNT'])
        elif 'OMPI_COMM_WORLD_SIZE' in os.environ:
            self.num_nodes = int(os.environ['OMPI_COMM_WORLD_SIZE'])
        elif 'AZUREML_NODE_COUNT' in os.environ:
            self.num_nodes = int(os.environ['AZUREML_NODE_COUNT'])
        else:
            self.num_nodes = 1

        if 'RANK' in os.environ:
            self.node_rank = int(os.environ['RANK'])
        elif 'OMPI_COMM_WORLD_RANK' in os.environ:
            self.node_rank = int(os.environ['OMPI_COMM_WORLD_RANK'])
        elif 'AZ_BATCHAI_TASK_INDEX' in os.environ:
            self.node_rank = int(os.environ['AZ_BATCHAI_TASK_INDEX'])
        else:
            self.node_rank = 0

        self.local_run = local_run
        self.seed0 = seed0

        self.builder_snapshot = deepcopy(self.__class__.__builder__)

    def __call__(self):
        num_gpus = torch.cuda.device_count()
        # _single_thread_run(0, 1, self)
        torch.multiprocessing.spawn(
            _single_thread_run, args=(num_gpus, self), nprocs=num_gpus, join=True)
