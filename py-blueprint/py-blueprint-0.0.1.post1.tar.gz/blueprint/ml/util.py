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
import numpy as np

import torch
import torch.nn as nn
import torch.distributed as dist

from typing import Optional, Dict, List
from packaging import version
import collections
import pickle as pk
import yaml
import shutil
import contextlib
import time

from .inference import BatchList
from .logger import Logger

_PYTORCH_VERSION_NEWER_THAN_180_ = version.parse(
    torch.__version__) >= version.parse('1.8.0')
if _PYTORCH_VERSION_NEWER_THAN_180_:
    def barrier():
        """The new version.
        """
        dist.barrier(device_ids=[torch.cuda.current_device()])
else:
    def barrier():
        """The old version.
        """
        dist.barrier()


FRAMEWORK_ROOT = os.path.abspath(os.path.dirname(__file__))


def _load_states(states_dir, logger: Logger,
                 global_step: Optional[int] = None,
                 epoch: Optional[int] = None):
    if not os.path.exists(states_dir):
        logger.log_info('%s does not exist' % states_dir)
        return None

    selected_filename = None
    if global_step is not None or epoch is not None:
        for n in os.listdir(states_dir):
            if not n.startswith('_') and n.endswith('.pth'):
                try:
                    step_str, epoch_str = n[:-len('.pth')].split('_')
                    _step = int(step_str)
                    _epoch = int(epoch_str)
                    if _step == global_step or _epoch == epoch:
                        selected_filename = os.path.join(states_dir, n)
                except:
                    continue
    if selected_filename is not None:
        logger.log_info('loading states from %s' % selected_filename)
        return torch.load(
            open(selected_filename, 'rb'),
            map_location={'cuda:0': f'cuda:{torch.cuda.current_device()}'})

    logger.log_info('locating the latest loadable state ...')
    state_files = [os.path.join(states_dir, n)
                   for n in os.listdir(states_dir)
                   if not n.startswith('_') and n.endswith('.pth')]
    state_files.sort(key=os.path.getmtime)

    for filename in state_files[::-1]:
        try:
            logger.log_info('loading states from %s' % filename)
            return torch.load(
                open(filename, 'rb'),
                map_location={'cuda:0': f'cuda:{torch.cuda.current_device()}'})
        except Exception as e:
            logger.log_info('Exception: %s' % e)
    logger.log_info('no valid state files found in %s' % states_dir)
    return None


def _save_states(state_dict: dict, states_dir: str, losses: Dict[str, float],
                 global_step: int, epoch: int, num_states_kept: Optional[int],
                 always_kept_steps: List[int], always_kept_epoches: List[int],
                 logger: Logger):

    assert num_states_kept is None or num_states_kept > 1
    if not os.path.exists(states_dir):
        os.makedirs(states_dir)

    # load existing records
    records_filename = os.path.join(states_dir, '_records.pth')
    if os.path.exists(records_filename):
        records = torch.load(records_filename)
    else:
        records = dict()

    # update records
    for loss_name, loss in losses.items():
        if loss_name not in records:
            records[loss_name] = (global_step, epoch, loss)
        else:
            _, _, prev_loss = records[loss_name]
            if loss < prev_loss:
                records[loss_name] = (global_step, epoch, loss)

    def _filename_overwritable(fn: str) -> bool:
        if not fn.endswith('.pth'):
            return False
        if fn.startswith('_'):
            return False

        _step = None
        _epoch = None
        try:
            step_str, epoch_str = fn[:-len('.pth')].split('_')
            _step = int(step_str)
            _epoch = int(epoch_str)
        except:
            return False

        if _step in always_kept_steps or _epoch in always_kept_epoches:
            return False
        for _, (s, e, _) in records.items():
            if (s, e) == (_step, _epoch):
                # this means (_step, _epoch) is stored in records
                return False
        return True

    overwritable_state_files = [os.path.join(states_dir, n)
                                for n in os.listdir(states_dir)
                                if _filename_overwritable(n)]
    overwritable_state_files.sort(key=os.path.getmtime)
    if num_states_kept is not None:
        logger.log_info(f'{len(overwritable_state_files)} state files are '
                        f'overwritable in folder {states_dir} '
                        f'will only keeping {num_states_kept} states')

    filename_to_save = os.path.join(
        states_dir, f'{global_step}_{epoch}.pth')
    if num_states_kept is None or len(overwritable_state_files) < num_states_kept:
        torch.save(state_dict, filename_to_save)
    else:
        earliest_file = overwritable_state_files[0]
        torch.save(state_dict, open(earliest_file, 'wb'))
        os.rename(earliest_file, filename_to_save)
    logger.log_info('state saved to %s' % filename_to_save)

    for loss_name, (s, e, v) in records.items():
        logger.log_info(('The best state for loss %s is in '
                        '%d_%d.pth with value %f') %
                        (loss_name, s, e, v))

    # save records
    torch.save(records, records_filename)
    logger.log_info('records saved to %s' % records_filename)


def to_descriptors(data):
    if isinstance(data, BatchList):
        return BatchList([to_descriptors(val) for val in data.values])
    if isinstance(data, collections.abc.Mapping):
        return {key: to_descriptors(val) for key, val in data.items()}
    elif isinstance(data, tuple) and hasattr(data, '_fields'):  # namedtuple
        return type(data)(*(to_descriptors(val) for val in data))
    elif isinstance(data, collections.abc.Sequence):
        return [to_descriptors(val) for val in data]
    elif isinstance(data, torch.Tensor):
        return f'torch.Tensor[dtype={data.dtype}, size={tuple(data.shape)}]'
    elif isinstance(data, np.ndarray):
        return f'np.ndarray[dtype={data.dtype}, size={tuple(data.shape)}]'
    else:
        return type(data)


def get_submodule(m: nn.Module, target: str) -> nn.Module:
    if target == "":
        return m

    atoms: List[str] = target.split(".")
    mod: nn.Module = m

    for item in atoms:
        if not hasattr(mod, item):
            raise AttributeError(mod._get_name() + " has no "
                                 "attribute `" + item + "`")
        mod = getattr(mod, item)
        if not isinstance(mod, nn.Module):
            raise AttributeError("`" + item + "` is not "
                                 "an nn.Module")
    return mod


def accumulate(model1: nn.Module, model2: nn.Module, decay: float):
    """Accumulate model2 to model1.

    model1 = model1 * decay + model2 * (1 - decay)
    """
    par1 = dict(model1.named_parameters())
    par2 = dict(model2.named_parameters())

    for k in par1.keys():
        par1[k].data.mul_(decay).add_(
            other=par2[k].data.to(par1[k].data.device),
            alpha=1 - decay)

    par1 = dict(model1.named_buffers())
    par2 = dict(model2.named_buffers())

    for k in par1.keys():
        if par1[k].data.is_floating_point():
            par1[k].data.mul_(decay).add_(
                other=par2[k].data.to(par1[k].data.device),
                alpha=1 - decay)
        else:
            par1[k].data = par2[k].data.to(par1[k].data.device)


def all_gather(data):
    """
    Run all_gather on arbitrary picklable data (not necessarily tensors)
    Args:
        data: any picklable object
    Returns:
        list[data]: list of data gathered from each rank
    """
    world_size = dist.get_world_size()
    if world_size == 1:
        return [data]

    # serialized to a Tensor
    buffer = pk.dumps(data)
    storage = torch.ByteStorage.from_buffer(buffer)
    tensor = torch.ByteTensor(storage).to("cuda")

    # obtain Tensor size of each rank
    local_size = torch.LongTensor([tensor.numel()]).to("cuda")
    size_list = [torch.LongTensor([0]).to("cuda") for _ in range(world_size)]
    dist.all_gather(size_list, local_size)
    size_list = [int(size.item()) for size in size_list]
    max_size = max(size_list)

    # receiving Tensor from all ranks
    # we pad the tensor because torch all_gather does not support
    # gathering tensors of different shapes
    tensor_list = []
    for _ in size_list:
        tensor_list.append(torch.ByteTensor(size=(max_size,)).to("cuda"))
    if local_size != max_size:
        padding = torch.ByteTensor(size=(max_size - local_size,)).to("cuda")
        tensor = torch.cat((tensor, padding), dim=0)
    dist.all_gather(tensor_list, tensor)

    data_list = []
    for size, tensor in zip(size_list, tensor_list):
        buffer = tensor.cpu().numpy().tobytes()[:size]
        data_list.append(pk.loads(buffer))

    return data_list


def all_gather_by_part(lst: list, size: Optional[int]) -> list:
    if dist.get_rank() == 0:
        print(f'local list length: {len(lst)}')

    if size is None:
        result = sum(all_gather(lst), [])
    else:
        def _get_subset(i, data, size) -> list:
            start = min(i * size, len(data))
            stop = min(start + size, len(data))
            return data[start:stop]
        # get max length
        length = torch.tensor(len(lst), dtype=torch.int32, device='cuda')
        dist.all_reduce(length, dist.ReduceOp.MAX)
        length = length.cpu().item()
        # print(f'max local length: {length}')
        result = []
        for i in range((length+size-1) // size):
            gathered = sum(all_gather(_get_subset(i, lst, size)), [])
            result += gathered

    if dist.get_rank() == 0:
        print(f'gathered list length: {len(result)}')
    return result


def path_is_parent(parent_path: str, child_path: str) -> str:
    # Smooth out relative path names, note: if you are concerned about symbolic links,
    # you should use os.path.realpath too
    parent_path = os.path.abspath(parent_path)
    child_path = os.path.abspath(child_path)

    # Compare the common path of the parent and child path with the common path of just
    # the parent path. Using the commonpath method on just the parent path will regularise
    # the path name in the same way as the comparison that deals with both paths,
    # removing any trailing path separator
    return os.path.commonpath([parent_path]) == os.path.commonpath([parent_path, child_path])


def get_connection_string(blob_root, container_name: str) -> str:
    blob_config = yaml.safe_load(
        open(os.path.join(blob_root, 'config', 'blob.yaml'), 'r'))
    return blob_config[container_name]['connection_string']


def get_query_string(blob_root, container_name: str) -> str:
    blob_config = yaml.safe_load(
        open(os.path.join(blob_root, 'config', 'blob.yaml'), 'r'))
    return blob_config[container_name]['query_string']


def download(blob_root: str, remote_path: str, local_path: str):
    """
    Args:
        remote_path (str): e.g ':blob/haya/xxx', or some regular path.
        local_path (str): a regular local path.
    """
    if remote_path.startswith(':blob/'):
        _, container_name, *path = remote_path.split('/')
        sig = get_query_string(blob_root, container_name)
        path = os.path.join(*path)

        print(f"Downloading {path} from container_name {container_name} ...")
        os.environ['AZCOPY_CRED_TYPE'] = 'Anonymous'
        azcopy_exe = os.path.join(blob_root, 'tool', 'aml', 'azcopy')
        os.system(f'{azcopy_exe} copy '
                  f'"https://facevcstandard.blob.core.windows.net/{container_name}/'
                  f'{path}?{sig}" '
                  f'"{local_path}" --overwrite=true --check-md5 FailIfDifferent '
                  f'--from-to=BlobLocal --recursive --trusted-microsoft-suffixes= --log-level=ERROR')
        os.environ['AZCOPY_CRED_TYPE'] = ''
        print('Done')

    else:
        shutil.copy(remote_path, local_path)


def deal_with_remote_file(remote_path: str, copy2local: bool, blob_root: str) -> str:
    if not copy2local and not remote_path.startswith(':blob/'):
        return remote_path

    if dist.is_initialized():
        local_model_path = os.path.basename(remote_path)
        if not os.path.exists(local_model_path) and torch.cuda.current_device() == 0:
            print(
                f'Copying {remote_path} to local directory {local_model_path}')
            download(blob_root, remote_path, local_model_path)
        barrier()
        return local_model_path
    else:
        local_model_path = os.path.basename(remote_path)
        if not os.path.exists(local_model_path):
            print(
                f'Copying {remote_path} to local directory {local_model_path}')
            download(blob_root, remote_path, local_model_path)
        return local_model_path


def dir_nonempty(dirname):
    # If directory exists and nonempty (ignore hidden files), prompt for action
    return os.path.isdir(dirname) and len([x for x in os.listdir(dirname) if x[0] != '.'])


def query_dir(d):
    if dir_nonempty(d):
        key = input(f'{d} is not empty, delete it? (y/N): ')
        if key == 'y':
            import shutil
            shutil.rmtree(d)
            return True
        else:
            return False
    else:
        return True


def try_mkdir(d):
    if not os.path.exists(d):
        os.mkdir(d)


def try_makedirs(d):
    if not os.path.exists(d):
        os.makedirs(d)


def read_name_list(filename):
    names = []
    for name in open(filename, 'r'):
        name = name.strip()
        if len(name) > 0:
            names.append(name)
    return names


def write_name_list(filename, names):
    with open(filename, 'w') as f:
        for name in names:
            f.write(name + '\n')


@contextlib.contextmanager
def record_time(name, collect_dict=None):
    start = time.time()
    yield
    stop = time.time()
    if collect_dict is None:
        print('time cost of %s is %f seconds' %
              (name, stop-start))
    else:
        collect_dict[f'{name}(s)'] = stop-start
