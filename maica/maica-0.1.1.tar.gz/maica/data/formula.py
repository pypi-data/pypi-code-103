import numpy
import copy
import torch
from tqdm import tqdm
from chemparse import parse_formula
from sklearn.preprocessing import scale
from maica.core.env import *
from maica.data.base import NumericalData
from maica.data.base import NumericalDataset
from maica.data.util import read_data_file
from maica.data.util import impute
from maica.chem.base import load_elem_feats
from maica.chem.formula import get_compact_form_vec
from maica.chem.formula import get_sparse_form_vec
from maica.chem.formula import get_dop_form_vec


class FormData(NumericalData):
    def __init__(self,
                 x: object,
                 y: object,
                 idx: int,
                 formula: str):
        super(FormData, self).__init__(x, y, idx)

        self._formula = copy.deepcopy(formula)
        self._tooltip += ', Chemical formula: {}'.format(self.formula)

    def __str__(self):
        return 'Data object: <index: {}, formula: {}, x: {}, y: {}>'.\
            format(str(self.idx), self.formula, str(self.x), str(self.y))

    @property
    def formula(self):
        return self._formula


class DopFormData(FormData):
    def __init__(self,
                 host_x: object,
                 dop_x: object,
                 y: object,
                 idx: int,
                 formula: str):
        super(DopFormData, self).__init__(numpy.hstack([host_x, dop_x]), y, idx, formula)
        self.host_x = copy.deepcopy(host_x)
        self.dop_x = copy.deepcopy(dop_x)
        self.__n_host_feats = self.host_x.shape[0]
        self.__n_dop_feats = self.dop_x.shape[0]

    @property
    def n_host_feats(self):
        return self.__n_host_feats

    @property
    def n_dop_feats(self):
        return self.__n_dop_feats

    def normalize_x(self,
                    mean: object,
                    std: object):
        if isinstance(self.x, numpy.ndarray):
            self.x = (self.x - mean) / std
        elif isinstance(self.x, torch.Tensor):
            self.x = (self.x - mean) / std
        else:
            raise AssertionError('Unknown data type of the input data.')

        self.host_x = copy.deepcopy(self.x[:self.n_host_feats])
        self.dop_x = copy.deepcopy(self.x[self.n_host_feats:])

    def denormalize_x(self,
                      mean: object,
                      std: object):
        if isinstance(self.x, numpy.ndarray):
            self.x = std * self.x + mean
        elif isinstance(self.x, torch.Tensor):
            self.x = std * self.x + mean
        else:
            raise AssertionError('Unknown data type of the input data.')

        self.host_x = copy.deepcopy(self.x[:self.n_host_feats])
        self.dop_x = copy.deepcopy(self.x[self.n_host_feats:])

    def to_numpy(self):
        self.x = self.x.numpy()
        self.host_x = copy.deepcopy(self.x[:self.n_host_feats])
        self.dop_x = copy.deepcopy(self.x[self.n_host_feats:])

        if self.y is not None:
            self.y = self.y.numpy()

    def to_tensor(self):
        self.x = torch.tensor(self.x, dtype=torch.float)
        self.host_x = copy.deepcopy(self.x[:self.n_host_feats])
        self.dop_x = copy.deepcopy(self.x[self.n_host_feats:])

        if self.y is not None:
            self.y = torch.tensor(self.y, dtype=torch.float)


class FormDataset(NumericalDataset):
    def __init__(self,
                 data: list,
                 idx_form: object,
                 idx_feat: object,
                 idx_target: int,
                 var_names: numpy.ndarray):
        super(FormDataset, self).__init__(data, idx_feat, idx_target, var_names)
        self.__idx_form = copy.deepcopy(idx_form)
        self._set_feat_info()

    @property
    def idx_form(self):
        return self.__idx_form

    def _set_feat_info(self):
        for idx in self.idx_form:
            self.feat_names.append(self.var_names[idx])
            self.feat_types.append(FEAT_TYPE_FORM)

        if self.idx_feat is not None:
            for idx in self.idx_feat:
                self.feat_names.append(self.var_names[idx])
                self.feat_types.append(FEAT_TYPE_NUM)


class DopFormDataset(FormDataset):
    def __init__(self,
                 data: list,
                 idx_form: object,
                 idx_feat: object,
                 idx_target: int,
                 var_names: numpy.ndarray,
                 max_dops: int,
                 dop_thr: float):
        super(DopFormDataset, self).__init__(data, idx_form, idx_feat, idx_target, var_names)
        self.host_x = self._collect_host_feats()
        self.dop_x = self._collect_dop_feats()
        self.__n_host_feats = self.host_x.shape[1]
        self.__n_dop_feats = self.dop_x.shape[1]
        self.__max_dops = max_dops
        self.__dop_thr = dop_thr

    @property
    def n_host_feats(self):
        return self.__n_host_feats

    @property
    def n_dop_feats(self):
        return self.__n_dop_feats

    @property
    def max_dops(self):
        return self.__max_dops

    @property
    def dop_thr(self):
        return self.__dop_thr

    def _update_input_data(self):
        self.x = self._collect_input_data()
        self.host_x = self._collect_host_feats()
        self.dop_x = self._collect_dop_feats()

    def _collect_host_feats(self):
        if isinstance(self.data[0].host_x, numpy.ndarray):
            return numpy.vstack([d.host_x for d in self.data])
        elif isinstance(self.data[0].host_x, torch.Tensor):
            return torch.vstack([d.host_x for d in self.data])
        else:
            raise AssertionError('Unknown data type of the host features.')

    def _collect_dop_feats(self):
        if isinstance(self.data[0].dop_x, numpy.ndarray):
            return numpy.vstack([d.dop_x for d in self.data])
        elif isinstance(self.data[0].dop_x, torch.Tensor):
            return torch.vstack([d.dop_x for d in self.data])
        else:
            raise AssertionError('Unknown data type of the dopant features.')


def load_form_dataset(path_data_file: str,
                      idx_form: object,
                      idx_feat: object = None,
                      idx_target: int = None,
                      path_elem_embs: str = None,
                      impute_method: str = IMPUTE_KNN,
                      rep_type: str = REP_COMPACT,
                      normalization: bool = False):
    __idx_form = numpy.atleast_1d(idx_form)
    __idx_feat = numpy.atleast_1d(idx_feat) if idx_feat is not None else idx_feat
    elem_feats = load_elem_feats(path_elem_embs)

    if rep_type == REP_COMPACT:
        return __load_compact_dataset(path_data_file, __idx_form, __idx_feat, idx_target, elem_feats,
                                      impute_method, normalization)
    elif rep_type == REP_SPARSE:
        return __load_sparse_dataset(path_data_file, __idx_form, __idx_feat, idx_target, elem_feats,
                                     impute_method, normalization)


def load_dop_form_dataset(path_data_file: str,
                          idx_form: object,
                          idx_feat: object = None,
                          idx_target: int = None,
                          path_elem_embs: str = None,
                          impute_method: str = IMPUTE_KNN,
                          max_dops: int = 3,
                          dop_thr: float = 0.1,
                          normalization: bool = False):
    __idx_form = numpy.atleast_1d(idx_form)
    __idx_feat = numpy.atleast_1d(idx_feat) if idx_feat is not None else idx_feat
    elem_feats = load_elem_feats(path_elem_embs)
    data_file, data_obj = read_data_file(path_data_file)
    numeric_feats = None if __idx_feat is None else impute(data_obj[:, __idx_feat], impute_method)
    targets = None if idx_target is None else data_obj[:, idx_target]
    data = list()

    if normalization:
        elem_feats = scale(elem_feats)

        if numeric_feats is not None:
            numeric_feats = scale(numeric_feats)

    for i in tqdm(range(0, data_obj.shape[0])):
        host_feats = list()
        dop_feats = list()

        for idx in __idx_form:
            host_feat, dop_feat = get_dop_form_vec(data_obj[i, idx], elem_feats, max_dops, dop_thr)
            host_feats.append(host_feat)
            dop_feats.append(dop_feat)
        host_feats = numpy.hstack(host_feats)
        dop_feats = numpy.hstack(dop_feats)
        formula = ' '.join([data_obj[i, idx] for idx in __idx_form])

        if numeric_feats is not None:
            host_feats = numpy.hstack([host_feats, numeric_feats[i, :]])

        if targets is None:
            data.append(DopFormData(host_x=host_feats, dop_x=dop_feats, y=None, idx=i, formula=formula))
        else:
            data.append(DopFormData(host_x=host_feats, dop_x=dop_feats, y=targets[i], idx=i, formula=formula))

    return DopFormDataset(data, __idx_form, __idx_feat, idx_target, data_file.columns.values, max_dops, dop_thr)


def __load_compact_dataset(path_data_file: str,
                           idx_form: numpy.ndarray,
                           idx_feat: numpy.ndarray,
                           idx_target: int,
                           elem_feats: numpy.ndarray,
                           impute_method: str,
                           normalization: bool = False):
    data_file, data_obj = read_data_file(path_data_file)
    numeric_feats = None if idx_feat is None else impute(data_obj[:, idx_feat], impute_method)
    targets = None if idx_target is None else data_obj[:, idx_target]
    data = list()

    if normalization:
        elem_feats = scale(elem_feats)

        if numeric_feats is not None:
            numeric_feats = scale(numeric_feats)

    for i in tqdm(range(0, data_obj.shape[0])):
        form_feats = numpy.hstack([get_compact_form_vec(data_obj[i, idx], elem_feats) for idx in idx_form])
        formula = ' '.join([data_obj[i, idx] for idx in idx_form])

        if numeric_feats is not None:
            form_feats = numpy.hstack([form_feats, numeric_feats[i, :]])

        if targets is None:
            data.append(FormData(x=form_feats, y=None, idx=i, formula=formula))
        else:
            data.append(FormData(x=form_feats, y=targets[i], idx=i, formula=formula))

    return FormDataset(data, idx_form, idx_feat, idx_target, data_file.columns.values)


def __load_sparse_dataset(path_data_file: str,
                          idx_form: numpy.ndarray,
                          idx_feat: numpy.ndarray,
                          idx_target: int,
                          elem_feats: numpy.ndarray,
                          impute_method: str,
                          normalization: bool = False):
    data_file, data_obj = read_data_file(path_data_file)
    numeric_feats = None if idx_feat is None else impute(data_obj[:, idx_feat], impute_method)
    targets = None if idx_target is None else data_obj[:, idx_target]
    forms = list()
    data = list()

    if normalization:
        elem_feats = scale(elem_feats)

        if numeric_feats is not None:
            numeric_feats = scale(numeric_feats)

    for i in range(0, data_obj.shape[0]):
        forms.append([parse_formula(data_obj[i, idx]) for idx in idx_form])
    max_elems = numpy.max([len(x.keys()) for d in forms for x in d])

    for i in tqdm(range(0, data_obj.shape[0])):
        form_feats = numpy.hstack([get_sparse_form_vec(data_obj[i, idx], elem_feats, max_elems) for idx in idx_form])
        numpy.set_printoptions(threshold=10000000000)
        formula = ' '.join([data_obj[i, idx] for idx in idx_form])

        if numeric_feats is not None:
            form_feats = numpy.hstack([form_feats, numeric_feats[i, :]])

        if targets is None:
            data.append(FormData(x=form_feats, y=None, idx=i, formula=formula))
        else:
            data.append(FormData(x=form_feats, y=targets[i], idx=i, formula=formula))

    return FormDataset(data, idx_form, idx_feat, idx_target, data_file.columns.values)
