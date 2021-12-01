import torch
import torch.distributed as dist


def init() -> None:
    if dist.is_mpi_available():
        backend = "mpi"
    elif (
        torch.cuda.is_available()
        and dist.is_nccl_available()
        and torch.cuda.device_cound() > 0
    ):
        backend = "nccl"
    elif dist.is_gloo_available():
        backend = "gloo"
    dist.init_process_group(backend)


def rank() -> int:
    return dist.get_rank()


def world_size() -> int:
    return dist.get_world_size()


def allreduce(tensor: torch.Tensor) -> torch.Tensor:
    dist.all_reduce(tensor)
    return tensor
