#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: DIYer22@github
@mail: ylxx@live.com
Created on Sat Jul 20 22:46:09 2019
"""
from boxx import *
from boxx import inpkg, SaveArguments

import numpy as np
import random

with inpkg():
    from .env import direction
    from .tools import iter_by_dpflow

identity = lambda x: x


try:
    import torch

    torch_dataset = torch.utils.data.Dataset
except ModuleNotFoundError:
    torch = ModuleNotFoundError
    torch_dataset = object


def recursive_func(func):
    def inner_func(batch, device=None):
        if isinstance(batch, dict):
            return {k: inner_func(v, device) for k, v in batch.items()}
        elif isinstance(batch, (list, tuple)):
            return type(batch)([inner_func(x, device) for x in batch])
        else:
            return func(batch, device=device)

    return inner_func


def to_tensor(x, device=None):
    if isinstance(x, np.ndarray):
        x = torch.from_numpy(x)
    if isinstance(x, torch.Tensor):
        x = x.cuda() if device is None else x.to(device)
    return x


batch_to_tensor = recursive_func(to_tensor)


def to_numpy(x, device=None):
    if isinstance(x, np.ndarray):
        return x
    if isinstance(x, torch.Tensor):
        x = x.detach().cpu().numpy()
    if getattr(x, "asnumpy", None):
        return x.asnumpy()
    return x


batch_to_numpy = recursive_func(to_numpy)


def dataloader_by_dpflow(dataloader, dpname, log=10, timeout=3600 * 36):
    # TODO make a fake dataloader that has same attributes with raw dataloader
    iterr = iter_by_dpflow(
        dataloader,
        dpname,
        direction,
        log=log,
        timeout=timeout,
        inputf=lambda batch: batch_to_tensor(batch, device="cpu"),
        outputf=batch_to_numpy,
    )
    if direction == "output":
        next(iterr)
    return iterr


def dataset_by_dpflow(dataset, dpname, log=10, timeout=3600 * 36):
    if direction == "input":
        dataset = DpflowDataset(dataset, dpname, log, timeout)
        return dataset
    if direction == "output":
        n = len(dataset)

        def dataset_iter_yield():
            while True:
                idx = int((n - 0.1) * random.random())
                data = dataset[idx]
                yield data

        iterr = iter_by_dpflow(
            dataset_iter_yield(),
            dpname,
            direction,
            log=log,
            timeout=timeout,
            outputf=batch_to_numpy,
        )
        next(iterr)
        raise Exception("Shold stop before.")
    raise Exception(f"Type should be in ['ouput', 'input']")


class DpflowDataset(torch_dataset):
    def __init__(self, dataset, dpname, log, timeout):
        self.dataset = dataset
        self.n = len(dataset)
        self.input_iter = SaveArguments(
            None,
            dpname,
            direction,
            log=log,
            timeout=timeout,
            inputf=lambda batch: batch_to_tensor(batch, device="cpu"),
        )

    def __len__(self):
        return int(self.n * 1e6)

    def __getitem__(self, idx):
        if isinstance(self.input_iter, SaveArguments):
            self.input_iter = self.input_iter.apply(iter_by_dpflow)
        return next(self.input_iter)


class DpflowDatasetMxnet(DpflowDataset):
    def __init__(self, dataset, dpname, log, timeout):
        DpflowDataset.__init__(self, dataset, dpname, log, timeout)
        self.input_iter = SaveArguments(
            None,
            dpname,
            direction,
            log=log,
            timeout=timeout,
            # inputf = lambda
        )

    def __len__(self):
        return int(self.n)


def dataset_by_dpflow_mxnet(dataset, dpname, log=10, timeout=3600 * 36):
    if direction == "input":
        dataset2 = DpflowDatasetMxnet(dataset, dpname, log, timeout)
        dataset.input_iter = dataset2.input_iter
        dataset.__getitem__ = dataset2.__getitem__
        dataset2.__dict__.update(dataset.__dict__)
        return dataset2
    if direction == "output":
        n = len(dataset)

        def dataset_iter_yield():
            while True:
                idx = int((n - 0.1) * random.random())
                data = dataset[idx]
                yield data

        iterr = iter_by_dpflow(
            dataset_iter_yield(),
            dpname,
            direction,
            log=log,
            timeout=timeout,
            outputf=batch_to_numpy,
        )
        next(iterr)
        raise Exception("Shold stop before.")
    raise Exception(f"Type should be in ['ouput', 'input']")


if __name__ == "__main__":
    pass
