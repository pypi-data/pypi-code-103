import numpy
import copy
import torch
from abc import ABC
from abc import abstractmethod
from sklearn.neighbors import LocalOutlierFactor
from maica.core.env import *
from maica.data.util import get_sub_list


class Data:
    def __init__(self,
                 x: object,
                 y: object,
                 idx: int):
        self.x = copy.deepcopy(x)
        self.y = None if y is None else numpy.array(y)
        self._idx = idx
        self._tooltip = 'Data index: {}'.format(self.idx)

    def __str__(self):
        return '<{} index: {}, x: {}, y: {}>'.format(type(self).__name__, str(self.idx), str(self.x), str(self.y))

    @property
    def idx(self):
        return self._idx

    @property
    def tooltip(self):
        return self._tooltip

    def normalize_y(self,
                    mean: object,
                    std: object):
        if isinstance(self.y, numpy.ndarray):
            self.y = numpy.array((self.y - mean) / std)
        elif isinstance(self.y, torch.Tensor):
            self.y = (self.y - mean) / std
        else:
            raise AssertionError('Unknown data type of the target data.')

    def denormalize_y(self,
                      mean: object,
                      std: object):
        if isinstance(self.y, numpy.ndarray):
            self.y = numpy.array(std * self.y + mean)
        elif isinstance(self.y, torch.Tensor):
            self.y = std * self.y + mean
        else:
            raise AssertionError('Unknown data type of the target data.')


class NumericalData(Data):
    def __init__(self,
                 x: object,
                 y: object,
                 idx: int):
        super(NumericalData, self).__init__(x, y, idx)

    def normalize_x(self,
                    mean: object,
                    std: object):
        if isinstance(self.x, numpy.ndarray):
            self.x = (self.x - mean) / std
        elif isinstance(self.x, torch.Tensor):
            self.x = (self.x - mean) / std
        else:
            raise AssertionError('Unknown data type of the input data.')

    def denormalize_x(self,
                      mean: object,
                      std: object):
        if isinstance(self.x, numpy.ndarray):
            self.x = std * self.x + mean
        elif isinstance(self.x, torch.Tensor):
            self.x = std * self.x + mean
        else:
            raise AssertionError('Unknown data type of the input data.')

    def to_numpy(self):
        self.x = self.x.numpy()

        if self.y is not None:
            self.y = self.y.numpy()

    def to_tensor(self):
        self.x = torch.tensor(self.x, dtype=torch.float)

        if self.y is not None:
            self.y = torch.tensor(self.y, dtype=torch.float)


class GraphData(Data):
    def __init__(self,
                 x: list,
                 y: object,
                 idx: int,
                 struct_id: str):
        super(GraphData, self).__init__(x, y, idx)
        self._struct_id = struct_id
        self._tooltip += ', Structure Id: {}'.format(self.struct_id)

    def __str__(self):
        return '<{}, index: {}, structure id: {}, x: {}, y: {}>'.\
            format(type(self).__name__, str(self.idx), self.struct_id, str(self.x), str(self.y))

    @property
    def struct_id(self):
        return self._struct_id


class Dataset(ABC):
    @abstractmethod
    def __init__(self,
                 data: list,
                 idx_feat: object,
                 idx_target: int,
                 var_names: numpy.ndarray):
        # Initialize the data object.
        self.data = copy.deepcopy(data)
        self.x = None
        self.y = None

        # Initialize metadata of the dataset.
        self.__idx_feat = copy.deepcopy(idx_feat)
        self.__idx_target = None if idx_target is None else copy.deepcopy(idx_target)
        self.__contain_target = False if self.idx_target is None else True
        self.__var_names = copy.deepcopy(var_names)
        self.__target_name = None if self.idx_target is None else self.var_names[self.idx_target]
        self._n_data = len(data)
        self._n_feats = None
        self._feat_names = list()
        self._feat_types = list()
        self._tooltips = self._collect_tooltips()

    @property
    def idx_feat(self):
        return self.__idx_feat

    @property
    def idx_target(self):
        return self.__idx_target

    @property
    def contain_target(self):
        return self.__contain_target

    @property
    def var_names(self):
        return self.__var_names

    @property
    def target_name(self):
        return self.__target_name

    @property
    def n_data(self):
        return self._n_data

    @property
    def n_feats(self):
        return self._n_feats

    @property
    def feat_names(self):
        return self._feat_names

    @property
    def feat_types(self):
        return self._feat_types

    @property
    def tooltips(self):
        return self._tooltips

    @abstractmethod
    def _set_feat_info(self):
        pass

    @abstractmethod
    def _update_data(self, new_data):
        pass

    def _update_target_data(self):
        self.y = self._collect_target_data()

    def _collect_target_data(self):
        if self.contain_target:
            if isinstance(self.data[0].y, numpy.ndarray):
                return numpy.vstack([d.y for d in self.data])
            elif isinstance(self.data[0].y, torch.Tensor):
                return torch.vstack([d.y for d in self.data])
            else:
                raise AssertionError('Unknown data type of the target data.')
        else:
            return None

    def _collect_tooltips(self):
        return [d.tooltip for d in self.data]

    def clone(self):
        return copy.deepcopy(self)

    def split(self,
              ratio: float):
        if ratio >= 1 or ratio <= 0:
            raise AssertionError('The radio must be in [0, 1], but the given ratio is {:.4f}'.format(ratio))

        n_dataset1 = int(ratio * self.n_data)
        idx_rand = numpy.random.permutation(self.n_data)
        idx_dataset1 = idx_rand[:n_dataset1]
        idx_dataset2 = idx_rand[n_dataset1:]

        # Clone the dataset objects.
        dataset1 = self.clone()
        dataset2 = self.clone()

        # Update the sub-datasets with the sampled sub-data.
        dataset1._update_data(get_sub_list(self.data, idx_dataset1))
        dataset2._update_data(get_sub_list(self.data, idx_dataset2))

        return dataset1, dataset2

    def get_k_folds(self,
                    k: int):
        idx_rand = numpy.random.permutation(self.n_data)
        n_data_subset = int(self.n_data / k)
        sub_datasets = list()

        # Get k-1 sub-datasets with the same size.
        for i in range(0, k-1):
            idx_sub_dataset = idx_rand[i*n_data_subset:(i+1)*n_data_subset]
            sub_dataset = self.clone()
            sub_dataset._update_data(get_sub_list(self.data, idx_sub_dataset))
            sub_datasets.append(sub_dataset)

        # Get the last sub-dataset containing all remaining data.
        idx_sub_dataset = idx_rand[(k-1)*n_data_subset:]
        sub_dataset = self.clone()
        sub_dataset._update_data(get_sub_list(self.data, idx_sub_dataset))
        sub_datasets.append(sub_dataset)

        return sub_datasets


class NumericalDataset(Dataset):
    @abstractmethod
    def __init__(self,
                 data: list,
                 idx_feat: object,
                 idx_target: int,
                 var_names: numpy.ndarray):
        super(NumericalDataset, self).__init__(data, idx_feat, idx_target, var_names)

        self.x = self._collect_input_data()
        self.y = self._collect_target_data()
        self._n_feats = self.x.shape[1]

        self._feat_means = None
        self._feat_stds = None

    @property
    def feat_means(self):
        return self._feat_means

    @property
    def feat_stds(self):
        return self._feat_stds

    @abstractmethod
    def _set_feat_info(self):
        pass

    def _update_data(self, new_data):
        self.data = copy.deepcopy(new_data)
        self._tooltips = self._collect_tooltips()
        self._n_data = len(self.data)
        self._update_input_data()
        self._update_target_data()

    def _update_input_data(self):
        self.x = self._collect_input_data()

    def _collect_input_data(self):
        if isinstance(self.data[0].x, numpy.ndarray):
            return numpy.vstack([d.x for d in self.data])
        elif isinstance(self.data[0].x, torch.Tensor):
            return torch.vstack([d.x for d in self.data])
        else:
            raise AssertionError('Unknown data type of the input data.')

    def normalize(self):
        if isinstance(self.x, numpy.ndarray):
            self._feat_means = numpy.mean(self.x, axis=0)
            self._feat_stds = numpy.std(self.x, axis=0) + 1e-6
        elif isinstance(self.x, torch.Tensor):
            self._feat_means = torch.mean(self.x, dim=0)
            self._feat_stds = torch.std(self.x, dim=0) + 1e-6

        for i in range(0, self.n_data):
            self.data[i].normalize_x(self.feat_means, self.feat_stds)
        self._update_input_data()

    def denormalize(self):
        if self.feat_means is None:
            raise AssertionError('The input data of this dataset has not been normalized.')

        for i in range(0, self.n_data):
            self.data[i].denormalize_x(self.feat_means, self.feat_stds)
        self._update_input_data()

        self._feat_means = None
        self._feat_stds = None

    def to_numpy(self):
        for i in range(0, self.n_data):
            self.data[i].to_numpy()
        self._update_input_data()
        self._update_target_data()

    def to_tensor(self):
        for i in range(0, self.n_data):
            self.data[i].to_tensor()
        self._update_input_data()
        self._update_target_data()

    def remove_outliers(self):
        if not isinstance(self.x, numpy.ndarray):
            raise AssertionError('Outlier removal is supported only for numpy.ndarray object. '
                                 'Call to_numpy() method before executing this method.')

        lof = LocalOutlierFactor(n_neighbors=int(numpy.sqrt(self.n_data)))
        ind = lof.fit_predict(self.x)

        new_data = [self.data[i] for i in range(0, self.n_data) if ind[i] == 1]
        self._update_data(new_data)


class GraphDataset(Dataset):
    def __init__(self,
                 data: list,
                 idx_struct: object,
                 idx_feat: object,
                 idx_target: int,
                 var_names: numpy.ndarray):
        super(GraphDataset, self).__init__(data, idx_feat, idx_target, var_names)

        self.x = self._collect_input_data()
        self.y = self._collect_target_data()
        self.__idx_struct = copy.deepcopy(idx_struct)

    @property
    def idx_struct(self):
        return self.__idx_struct

    def _set_feat_info(self):
        for idx in self.idx_struct:
            self._feat_names.append(self.var_names[idx])
            self._feat_types.append(FEAT_TYPE_STRUCT)

        for idx in self.idx_feat:
            self._feat_names.append(self.var_names[idx])
            self._feat_types.append(FEAT_TYPE_NUM)

    def _update_data(self, new_data):
        self.data = copy.deepcopy(new_data)
        self._tooltips = self._collect_tooltips()
        self._n_data = len(self.data)
        self._update_input_data()
        self._update_target_data()

    def _update_input_data(self):
        self.x = self._collect_input_data()

    def _collect_input_data(self):
        return [d.x for d in self.data]
