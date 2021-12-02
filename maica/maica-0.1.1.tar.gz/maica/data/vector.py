import numpy
from tqdm import tqdm
from sklearn.preprocessing import scale
from maica.core.env import *
from maica.data.base import NumericalData
from maica.data.base import NumericalDataset
from maica.data.util import read_data_file
from maica.data.util import impute


class VectorDataset(NumericalDataset):
    def __init__(self,
                 data: list,
                 idx_feat: object,
                 idx_target: int,
                 var_names: numpy.ndarray):
        super(VectorDataset, self).__init__(data, idx_feat, idx_target, var_names)
        self._set_feat_info()

    def _set_feat_info(self):
        for idx in self.idx_feat:
            self._feat_names.append(self.var_names[idx])
            self._feat_types.append(FEAT_TYPE_NUM)


def load_vec_dataset(path_data_file: str,
                     idx_feat: object,
                     idx_target: int = None,
                     impute_method: str = IMPUTE_KNN,
                     normalization: bool = False):
    __idx_feat = numpy.atleast_1d(idx_feat)
    data_file, data_obj = read_data_file(path_data_file)
    input_feats = impute(data_obj[:, __idx_feat], impute_method)
    targets = None if idx_target is None else data_obj[:, idx_target]
    data = list()

    if normalization:
        input_feats = scale(input_feats)

    if targets is None:
        for i in tqdm(range(0, input_feats.shape[0])):
            data.append(NumericalData(x=input_feats[i, :], y=None, idx=i))
    else:
        for i in tqdm(range(0, input_feats.shape[0])):
            data.append(NumericalData(x=input_feats[i, :], y=targets[i], idx=i))

    return VectorDataset(data, __idx_feat, idx_target, data_file.columns.values)
