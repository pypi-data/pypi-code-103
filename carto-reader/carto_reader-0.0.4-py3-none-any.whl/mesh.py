"""
Mesh information

Josselin Duchateau, IHU Liryc
Last updated 06/12/2021
"""
from dataclasses import dataclass
import numpy as np
from collections.abc import MutableMapping
from typing import List


# Colormaps for the default mesh maps
DEFAULT_COLORMAPS = {
    'unipolar': ('gist_rainbow', [1.5, 5]),
    'bipolar': ('gist_rainbow', [0.5, 1.5]),
    'lat': ('hsv', None),
    'groupid': ('tab20', None)
}


@dataclass
class MeshAttributes:
    """ Attributes of the mesh """
    MeshID: int
    MeshName: str
    NumVertex: int
    NumTriangle: int
    TopologyStatus: int
    MeshColor: List[float]
    Matrix: List[float]
    NumVertexColors: int
    ColorsIDs: List[int]
    ColorsNames: List[str]
    NumVertexInitial: int = None
    NumTriangleInitial: int = None
    NumVisibleGroups: int = None
    VisibleGroupsIDs: List[int] = None
    VisibleGroupsTypes: List[int] = None
    NumTransparentGroups: int = None
    TransparentGroupsIDs: List[int] = None
    TransparentGroupsTypes: List[int] = None


class Mesh(MutableMapping):
    """ A class containing Carto FAM meshes and colormaps"""
    def __init__(self, vertices: np.ndarray = None, triangles: np.ndarray = None,
                 vertice_normals: np.ndarray = None, triangle_normals: np.ndarray = None,
                 attributes=None):
        self.v = vertices
        self.t = triangles
        self.vn = vertice_normals
        self.tn = triangle_normals

        self.attributes = attributes
        self._maps = {}

    @classmethod
    def from_file(cls, data_source, filename):
        """ Read a mesh from a file """
        if filename not in data_source.listdir():
            raise ValueError('Requested mesh not found in datasource.')

        def listify(value_string):
            """ Turn into a lsit"""
            item_list = value_string.strip().split()
            if not item_list:
                return None

            try:
                item_list = [int(item) for item in item_list]
            except ValueError:
                try:
                    item_list = [float(item) for item in item_list]
                except ValueError:
                    pass
            if len(item_list) == 1:
                return item_list[0]

            return item_list

        def read_attributes(_f):
            """ Read the attrivutes section """
            attributes = {}
            for _line in _f:
                _line = _line.decode('utf-8').rstrip()
                if not _line:
                    break
                if _line[0] == ';':
                    continue
                name, value = _line.split('=')
                attributes[name.strip()] = listify(value)
            return MeshAttributes(**attributes)

        def line_filter(_f):
            """ Filter line """
            got_data = False
            for _line in _f:
                if not _line.rstrip():
                    if got_data:
                        return
                    else:
                        continue
                if _line[0:1] == b';':
                    continue
                _line = _line.replace(b'=', b' ')
                got_data = True
                yield _line

        obj = cls()
        maps = None
        v_attributes = None
        with data_source.open(filename) as f:
            for line in f:
                line = line.rstrip()
                if line == b'[GeneralAttributes]':
                    obj.attributes = read_attributes(f)
                if line == b'[VerticesSection]':
                    vertices = np.loadtxt(line_filter(f))
                    obj.v = vertices[:, 1:4]
                    obj.vn = vertices[:, 4:7]
                    # obj._maps['vGroupID'] = vertices[:, 7]  # Vertex group info doesn't contain any data usually...
                if line == b'[TrianglesSection]':
                    triangles = np.loadtxt(line_filter(f))
                    obj.t = triangles[:, 1:4].astype(int)
                    obj.tn = triangles[:, 4:7]
                    group_id = -triangles[:, 7].astype(int)
                    group_id[group_id == 1000000] = -1
                    obj._maps['GroupID'] = group_id
                if line == b'[VerticesColorsSection]':
                    maps = np.loadtxt(line_filter(f))
                    maps[maps == -10000.] = np.nan
                if line == b'[VerticesAttributesSection]':
                    v_attributes = np.loadtxt(line_filter(f), dtype=int)

        if obj.attributes.ColorsNames is not None and maps is not None:
            for map, map_name in zip(maps.transpose()[1:], obj.attributes.ColorsNames):
                obj._maps[map_name] = map
        if v_attributes is not None:
            obj._maps['Scar'] = v_attributes.transpose()[1]
            obj._maps['EML'] = v_attributes.transpose()[2]
        return obj

    def add_map(self, map: np.ndarray, map_name=None):
        """ Add a map """
        if map.shape[1] != self.num_v or map.shape[1] != self.num_t:
            raise ValueError('Map must have the same size as number of vertices or triangles.')

        if map_name is None:
            i_map = 0
            map_name = 'UNNAMED 0'
            while map_name in self:
                i_map += 1
                map_name = f'UNNAMED {i_map}'

        self._maps[map_name] = map

    @property
    def num_v(self):
        """ Number of vertices """
        return self.v.shape[0]

    @property
    def num_t(self):
        """ Number of triangles (simplexes) """
        return self.t.shape[0]

    def __len__(self):
        return self._maps.__len__()

    def __getitem__(self, item):
        if isinstance(item, int):
            item = list(self.keys())[item]
        return self._maps.__getitem__(item)

    def __delitem__(self, key):
        if isinstance(key, int):
            key = list(self.keys())[key]
        return self._maps.__delitem__(key)

    def __setitem__(self, key, value):
        if isinstance(key, int):
            key = list(self.keys())[key]
        if not isinstance(value, np.ndarray):
            _value = np.ndarray(value)
        else:
            _value = value
        if value.shape[1] != self.num_v | value.shape[1] != self.num_t:
            raise ValueError('Input map has an invalid number of values')
        return self._maps.__setitem__(key, value)

    def __iter__(self):
        return self._maps.__iter__()

    def __repr__(self):
        return f'<Mesh ({self.num_v} x {self.num_t}), {len(self)} Maps>'

    def plot(self, _map=None):
        """ Plot the mesh """
        try:
            import pyvista as pv
        except ImportError:
            raise ImportError('Pyvista must be installed to plot meshes. '
                              'Use pip install carto_reader[viz] to install visualization dependencies.')

        tris = np.hstack(np.concatenate((3 * np.ones((self.num_t, 1), dtype=int), self.t), 1))
        poly_data = pv.PolyData(self.v, tris)
        plotter = pv.Plotter()

        i = -1
        _map = _map if map is not None else np.zeros((self.num_v,))
        curr_mesh = plotter.add_mesh(poly_data, scalars=_map)
        curr_text = plotter.add_text('')

        def change_map(increment):
            def plot_map():
                nonlocal i, curr_text, curr_mesh
                i = (i + increment + len(self)) % len(self)
                map_name = list(self.keys())[i]
                cmap, clim = DEFAULT_COLORMAPS.get(map_name.lower(), (None, None))
                plotter.remove_actor(curr_mesh)
                curr_mesh = plotter.add_mesh(poly_data, scalars=self[i], cmap=cmap, clim=clim)
                plotter.remove_actor(curr_text)
                curr_text = plotter.add_text(map_name)
            return plot_map

        plotter.add_key_event('Left', change_map(-1))
        plotter.add_key_event('Right', change_map(1))
        plotter.show()
