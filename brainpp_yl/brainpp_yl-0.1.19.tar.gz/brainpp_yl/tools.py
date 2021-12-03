#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: DIYer22@github
@mail: ylxx@live.com
Created on Thu Mar 28 16:30:58 2019
"""
import boxx
from boxx import *
from boxx import localTimeStr, os, setTimeout

import numpy as np
from random import shuffle


def split_keys_by_replica(keys):
    """
    `bpp.split_keys_by_replica`: 在 replica 模式下, 自动划分 keys (数据集), 兼容非 replica 模式
    """
    from .env import replica_idx, replica_total

    keys = sorted(keys)
    if replica_total == 1:
        return keys
    keys = keys[replica_idx::replica_total]
    shuffle(keys)
    return keys


def iter_by_dpflow(
    iterable, dpname, direction, log=10, timeout=3600 * 36, outputf=None, inputf=None
):
    from boxx import timegap, tree
    from dpflow import control, InputPipe, OutputPipe

    if log:
        print("dpname:\n\t", dpname)
        print(
            f"monitor url:\n\t https://dpflow-monitor.iap.hh-b.brainpp.cn/?name={dpname}"
        )
    if direction == "input":
        q = InputPipe(dpname)
        with control(io=[q]):
            for data in q:
                if inputf is not None:
                    data = inputf(data)
                yield data
    elif direction == "output":
        q = OutputPipe(dpname)
        with control(io=[q]):
            while True:
                for i_iter, data in enumerate(iterable):
                    if log and timegap(log, dpname):
                        print(i_iter)
                        tree(data, deep=1)
                    if outputf is not None:
                        data = outputf(data)
                    q.put_pyobj(data, timeout=timeout)
    raise Exception("Type should be in ['ouput', 'input']")


def dpflow_input_iter(dpname, gap=0, log=0):
    input_iter = iter_by_dpflow(None, dpname, "input", log=log)
    for data in input_iter:
        yield data


_TEST_NORI = "s3://yl-share/tmp/brainpp_yl_test/test.nori"


class NoriPickleAndPut:
    none = object()

    def __init__(self, nori_path=_TEST_NORI):
        self.nori_path = nori_path

    def __enter__(self):
        import nori2

        self.w = nori2.remotewriteopen(self.nori_path)
        self.w.__enter__()
        return self

    def __exit__(self, typee, value, traceback):
        self.w.__exit__(typee, value, traceback)

    def pickle_and_put(self, data, filename=None):
        import pickle

        return self.w.put(pickle.dumps(data), filename=filename)

    put = pickle_and_put

    @staticmethod
    def test():
        nori = f"s3://yl-share/tmp/brainpp_yl_test/{localTimeStr()}.nori"
        print(nori_pickle_and_put(nori, "a"))
        print(nori_pickle_and_put(nori, "b"))
        print(nori_pickle_and_put(nori, None))
        with nori_pickle_and_put(nori) as w:
            for i in range(3):
                print(w.put(i))
        os.system(
            boxx.p
            / f"nori speedup {nori} --on && python -m brainpp_yl.check_nori {nori}"
        )


def nori_pickle_and_put(
    nori_path=_TEST_NORI, data=NoriPickleAndPut.none, filename=None
):
    instance = NoriPickleAndPut(nori_path)
    if data is NoriPickleAndPut.none:
        return instance
    with instance:
        return instance.pickle_and_put(data)


def bpycv_result_to_spp_nori(result):
    """
    Cover bpycv result to standard_product_perception nori fromat
    ```bash
    In [1]: tree(nori)
    └── /: dict  4
        ├── img: (512, 512, 3)uint8
        ├── inst: (512, 512)int32     # Cityscapes instanceIds 格式
        ├── depth: (512, 512)float32  # 单位 mm
        └── info: dict  2
            ├── K: (3, 3)float32      # 相机内参
            └── poses: dict  2        # instance id => RT
                ├── 1000: (3, 4)float32
                └── 2001: (3, 4)float32
    # 测试用例: s3://yl-share/tmp/spp/test-v1.nori
    ```
    """
    nori = {}
    nori["img"] = np.uint8(result["image"])
    nori["inst"] = np.int32(result["inst"])
    nori["depth"] = np.float32(result["depth"]) * 1000
    nori["info"] = info = {}

    info["K"] = np.float32(result["ycb_6d_pose"]["intrinsic_matrix"])
    # info['cam_RT'] = result['ycb_6d_pose']["cam_matrix_world"][:3]
    # info['environment'] = '/tmp/environment.hdr'
    info["poses"] = {}

    for idx, inst_id in enumerate(result["ycb_6d_pose"]["inst_ids"]):
        info["poses"][inst_id] = np.float32(result["ycb_6d_pose"]["poses"][..., idx])
    return nori


IN_RRUN = "IN_RRUN_BRAINPP_YL"


class rrun_manage:
    id2client = {}
    independents = set()

    @staticmethod
    def kill_all(include_independents=False):
        import rrun

        ids = set(rrun_manage.id2client)
        if not include_independents:
            ids -= rrun_manage.independents

        def _kill(runner_id):
            client = rrun_manage.id2client[runner_id]
            client.kill_runner(rrun.KillRunnerRequest(id=runner_id))

        for runner_id in ids:
            setTimeout(lambda: _kill(runner_id))

    @staticmethod
    def add(runner_id, client, independent=False):
        rrun_manage.id2client[runner_id] = client
        if independent:
            rrun_manage.independents.add(runner_id)

    @staticmethod
    def rlaunch_by_rrun(
        cpu=1,
        gpu=0,
        memory=1024,
        preemptible="no",
        priority="Medium",
        cmd="",
        log_dir="/tmp",
        independent=False,
        P=1,
    ):
        if os.environ.get(IN_RRUN):
            return
        import rrun

        preemptible_flags = {
            "best-effort": rrun.RunnerSpec.BestEffort,
            "yes": True,
            "no": False,
        }
        assert preemptible in preemptible_flags
        runner_ids = []
        for idx in range(P):
            # TODO use -P and preemptible=no
            spec = rrun.RunnerSpec()
            spec.name = "rrun " + localTimeStr()
            spec.commands[:] = cmd
            spec.log_dir = log_dir
            spec.scheduling_hint.group = ""  # Inherit from master
            spec.resources.cpu = cpu
            spec.resources.memory_in_mb = memory
            spec.preemptible_flag = preemptible_flags[preemptible]  # 1.7.3 及以上版本支持
            spec.priority = priority  # Default: 'Medium'. Change this in need
            spec.max_wait_time = 3600 * int(1e9)
            spec.minimum_lifetime = 24 * 3600 * int(1e9)
            spec.capabilities[:] = [rrun.RunnerSpec.SYS_PTRACE]  # Default: empty

            os.environ[IN_RRUN] = "True"
            try:
                # Fill in several fields in runner spec from current environment.
                rrun.fill_runner_spec(
                    spec,
                    environments=True,  # Propagate environment variables to runner
                    uid_gid=True,  # Propagate linux uid and gids to runner
                    share_dirs=True,  # Propagate writability of share directories to runner
                    work_dir=True,  # Propagate current working directory to runner
                )
            finally:
                os.environ.pop(IN_RRUN)
            client = rrun.Client()
            response = client.start_runner(rrun.StartRunnerRequest(spec=spec))
            runner_id = response.id
            rrun_manage.add(runner_id, client, independent=independent)
            print(runner_id, ":", cmd)
            runner_ids.append(runner_id)
        return runner_ids


def tar_files(dic, tarpath):
    """
    dic {name: smart path}
    """
    import io
    import tqdm
    import tarfile
    from threading import Lock
    from megfile import smart_open

    if isinstance(dic, (list, tuple)):
        dic = {os.path.basename(path): path for path in dic}
    keys = sorted(dic)
    iterr = iter(tqdm.tqdm(keys))

    write_lock = Lock()

    with smart_open(tarpath, "wb") as f:
        with tarfile.open(fileobj=f, mode="w") as tar:

            def func(key_path):
                key, path = key_path
                byte = smart_open(path, "rb").read()
                info = tarfile.TarInfo(key)
                info.size = len(byte)
                byte_io = io.BytesIO(initial_bytes=byte)
                with write_lock:
                    tar.addfile(info, byte_io)
                    next(iterr)

            boxx.mapmt(func, dic.items(), pool=16)
    print("Save to:", tarpath)

    def test():
        paths = ["s3://yl-share/tmp/a.jpg", "s3://yl-share/tmp/aa.jpg"]
        tarpath = "s3://yl-share/tmp/test.tar"
        tar_files(paths, tarpath)


if __name__ == "__main__":
    pass
