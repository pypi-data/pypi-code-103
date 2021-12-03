
from ._utils import raise_dataobject as rd
from pathlib import Path
import numpy as np, sys, pandas as pd, os
from subprocess import Popen, PIPE
self_file_dir_path = Path(__file__).parent.resolve()
self_tmp_dir_path = Path(self_file_dir_path, "tmp")
if not os.path.exists(self_tmp_dir_path):
    os.mkdir(self_tmp_dir_path)
self_exec_dir_papth = Path(self_file_dir_path, "exec")
self_tmp_path = Path(self_tmp_dir_path, "tmp.csv")
import platform
if platform.system() == "Windows":
    self_exec_path = Path(self_exec_dir_papth, "mrmr.exe")
else:
    self_exec_path = Path(self_exec_dir_papth, "mrmr")

class MRMR(object):

    def __init__(self, method="penglab"):
        self.method = method

    def fit(self, dataobject):
        rd(dataobject)
        if self.method == "penglab":
            self.feature_mrmr = self.penglab(dataobject.X, dataobject.Y)
        return self

    def transform(self, dataobject, max_f=None):
        rd(dataobject)
        if max_f is None:
            max_f = dataobject.X.shape[1]
        else:
            max_f = max_f - 1
        mask = self.feature_mrmr[:max_f+1, 0].astype(int)
        dataobject.X = dataobject.X[:, mask]
        dataobject.Xnames = dataobject.Xnames[mask]
        return dataobject

    def fit_transform(self, dataobject, max_f=None):
        self.fit(dataobject)
        return self.transform(dataobject, max_f)


    def spliter(self):
        if platform.system() == "Windows":
            return "\r\n"
        else:
            return "\n"

    def penglab(self, X, Y):
        spliter = self.spliter()
        dataset = np.concatenate([Y.reshape(-1, 1), X], axis=1)
        dataset = pd.DataFrame(dataset)
        dataset.to_csv(self_tmp_path, index=None)
        cmd = f"\"{str(self_exec_path)}\" -i \"{str(self_tmp_path)}\" -t 1"
        out = Popen(cmd, stdout=PIPE)
        load_f = False
        feature_mrmr = []
        out = out.stdout.readlines()
        for o in out:
            t = o.decode()
            if t == f"{spliter}" and load_f:
                load_f = False
            if load_f:
                t = t.split(f"{spliter}")[0].split(" ")
                feature_mrmr.append([t[2], t[6]])
            if t == f"*** mRMR features *** {spliter}":
                load_f = True
        feature_mrmr.pop(0)
        feature_mrmr = np.array(feature_mrmr, dtype=float)
        feature_mrmr[:, 0] -= 1
        self_tmp_path.unlink()
        feature_mrmr = sorted(feature_mrmr.tolist(), key=lambda x: x[1], reverse=True)
        return np.array(feature_mrmr)