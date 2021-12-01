from typing import List, Tuple, Union, Dict, Any, Type, Generator, Optional
from dataclasses import dataclass
import os
import pandas as pd
import numpy as np
from matplotlib.colors import Colormap, Normalize
from actomyosin_analyser.file_io.data_reader import DataReader
from ..analysis.analyser import Analyser


class ExperimentIterator:

    def __init__(self, data_reader_class: Type[DataReader],
                 group_by: List[Tuple[pd.DataFrame, List[str]]],
                 simulation_folder_template: str, exclude: List[int],
                 data_file_suffix: str='data.h5'):

        index0 = group_by[0][0].index
        previous_groups = [GroupIterator(data_reader_class, index0, {}, simulation_folder_template)]
        for table, columns in group_by:
            assert (table.index == index0).all()
            for col in columns:
                _groups = []
                for group in previous_groups:
                    sim_indices = np.array([idx for idx in group.index if idx not in exclude])
                    if len(sim_indices) == 0:
                        continue
                    selected = table.loc[sim_indices]
                    for value in selected[col].unique():
                        new_values = group.values.copy()
                        new_values.update({col: value})
                        new_group = GroupIterator(
                            data_reader_class=data_reader_class,
                            index=selected.index[selected[col] == value],
                            values=new_values,
                            simulation_folder_template=simulation_folder_template,
                            data_file_suffix=data_file_suffix
                        )
                        _groups.append(new_group)
                previous_groups = _groups
        self.groups = previous_groups

    def __iter__(self):
        return iter(self.groups)

    def __len__(self):
        return len(self.groups)

    def get(self, **kwargs) -> List['GroupIterator']:
        selected = []
        for g in self.groups:
            if not g.has_matching_values(**kwargs):
                continue
            selected.append(g)
        return selected

    def create_index_from_groups(self) -> pd.Index:
        values = self.groups[0].values
        names = list(values.keys())
        arrays = []
        for n in names:
            arrays.append([g.values[n] for g in self.groups])
        if len(names) == 1:
            return pd.Index(arrays[0], name=names[0])
        return pd.MultiIndex.from_arrays(arrays, names=names)

    def assign_group_colors(
            self,
            key: str,
            colormap: Colormap,
            by_order: bool=True,
            norm: Optional[Normalize]=None
    ):
        if by_order:
            self._assign_group_colors_by_order(key, colormap)
        else:
            self._assign_group_colors_by_value(key, colormap, norm)

    def assign_group_labels(
            self,
            template_string: str,
            template_latex_label: Optional[str] = None
    ):
        for g in self.groups:
            g.label = template_string.format(**g.values)
            if template_latex_label:
                g.latex_label = template_latex_label.format(**g.values)
            else:
                g.latex_label = g.label

    def _assign_group_colors_by_order(self, key, colormap):
        sorted_values = sorted([g.values[key] for g in self.groups])
        for g in self.groups:
            g.color = colormap(sorted_values.index(g.values[key]))

    def _assign_group_colors_by_value(self, key, colormap, norm: Optional[Normalize]):
        if norm is None:
            raise RuntimeError("Norm has to be defined when using assign_group_colors by_value.")
        for g in self.groups:
            g.color = colormap(norm(g.values[key]))


class GroupIterator:

    def __init__(self,
                 data_reader_class: Type[DataReader],
                 index: Union[pd.Index, pd.MultiIndex],
                 values: Dict[str, Any],
                 simulation_folder_template: str,
                 data_file_suffix: str='data.h5',):
        self.data_reader_class = data_reader_class
        self.index = index
        self.values = values
        self._simulation_folder_template = simulation_folder_template
        self._data_file_suffix = data_file_suffix
        self.color = None
        self.label = None
        self.latex_label = None

    def __iter__(self):
        return self._generator()

    def __len__(self):
        return len(self.index)

    def _generator(self) -> Generator['Simulation', None, None]:
        for idx in self.index:
            path = self._simulation_folder_template.format(idx)
            dr = self.data_reader_class(os.path.join(path, self._data_file_suffix))
            yield Simulation(
                index=idx,
                path=path,
                data_reader=dr,
                analyser=Analyser(dr, os.path.join(path, 'analysis.h5'))
            )

    def has_matching_values(self, **kwargs):
        for key in kwargs:
            if key not in self.values:
                raise KeyError(f'Groups are not created with key {key}')
            if self.values[key] != kwargs[key]:
                return False
        return True

    def __repr__(self):
        return (f'GroupIterator: Index = {self.index}; '
                f'selected by values {self.values}')

    def __str__(self):
        return self.__repr__()

    def get_label_from_values(self) -> str:
        if len(self.values) is 0:
            return 'group_iterator_has_no_values'
        label = ''
        for key in self.values:
            v = self.values[key]
            label = label + key + '_' + str(v) + '_'
        return '_'.join(label[:-1].split())

    def __hash__(self):
        return hash(self.get_label_from_values())


@dataclass
class Simulation:
    index: int
    path: str
    data_reader: DataReader
    analyser: Analyser
