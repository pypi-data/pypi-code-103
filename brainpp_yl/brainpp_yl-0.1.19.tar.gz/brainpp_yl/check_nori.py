#!/usr/bin/env python3

import os
import boxx
import pickle
import nori2 as nori
from IPython import embed

if __name__ == "__main__":
    from boxx import *

    d = {}

    f = nori.Fetcher()
    args, kwargs = boxx.getArgvDic()
    if not len(args):
        print(
            "Usage: python -m brainpp_yl.check_nori s3://yl-share/tmp/ocrtoc_blender_tmp1.nori"
        )
        exit(-1)

    boxx.setTimeout(lambda: os.system(f"nori speedup {args[0]} --on"))

    cmd = f'nori ls "{args[0]}"'
    head_nori_str = boxx.execmd(cmd + " | head")

    def func():
        nori_str = boxx.execmd(cmd)
        d["nids"] = nori_str.split()
        d["print"] = f"Total {len(d['nids'])} nori_ids!"
        boxx.pblue(d["print"])
        boxx.pred(d["print"])

    t = boxx.setTimeout(func)
    nids = head_nori_str.split()
    for idx, nid in enumerate(nids):

        def get_func(idx=idx, nid=nid):
            pkl = f.get(nid)
            data = pickle.loads(pkl)
            print(f"{idx}/{len(nids)} data")
            boxx.tree(data, deep=1)
            globals()["data"] = data

        boxx.setTimeout(get_func)

    embed()
    t.join()
    print(d["print"])
