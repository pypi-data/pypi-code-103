"""module with tools for tekigo"""
# required for hdfdict related functions
from datetime import datetime
import yaml
import h5py
# required for GatherScatter
from scipy.sparse import csr_matrix
import numpy as np


__all__ = [
    "GatherScatter",
    "approx_vol_node_from_edge",
    "approx_edge_from_vol_node",
    "approx_vol_node_from_vol_cell",
    "approx_vol_cell_from_vol_node",
]


class GatherScatter:
    """
    Internal Class to hold the sparse gather matrix and do the sparse gather scatter
    Efficient implementation of unstructured mesh operations

    Originally created Feb 8th, 2018 by C. Lapeyre (lapeyre@cerfacs.fr)

    .. warning: the mesh MUST be composed of tetrahedrons

    :param connectivity: connectivity of the tetrahedral mesh (param 'tet->node' in .h5 mesh)
    :param operation_type: [**optional**] either **smooth** or **morph** (morphing operations)
    :type operation_type: string
    """

    def __init__(self, connectivity, operation_type="smooth"):
        """initialisation method of the class
        """
        self._ope = operation_type
        if self._ope == "smooth":
            self._elt = 4
            self._bincount = np.bincount(connectivity)
            # building gather matrix
            ncell = np.int_(connectivity.shape[0] / self._elt)
            nnode = np.max(connectivity) + 1
            #print("Ncell and Nnode = ", ncell, nnode)
            data = np.ones(connectivity.shape)
            indptr = np.arange(ncell + 1) * self._elt
            self.gather_matrix = csr_matrix(
                (data, connectivity, indptr), shape=(ncell, nnode)
            )
        elif self._ope == "morph":
            # reordering connectivity into cells shape
            self._tet2nde = np.reshape(connectivity, (-1, 4))
        else:
            raise ValueError("Operation type must be either 'smooth' or 'morph'")

    def smooth(self, field, passes=1):
        """method to do a smoothing of the given field (e.g. a criterion)

        :param field: field to be smoothed (node centered)
        :param passes: [**optional**] number of smoothing iterations
        :type passes: int

        :returns: smoothed field over nodes
        """

        for _ in range(passes):
            field = self.base_morph(field)

        return field

    def morph(self, field, morphing_type, passes=1):
        # pylint: disable=line-too-long
        """
        method to remorph the given field (which is scaled between 0 and 1) (e.g. a mask)

        :param field: field to be morphed (node centered)
        :param morphing_type: either one of the options below :

            - **dilate** to add a layer over all mask boundaries
            - **erode** to remove a layer over all mask boundaries
            - **open** to remove small isolated peaks, it is an *erode* then *dilate* of the given field
            - **close** to make small isolated peaks part of the mask , it is an *dilate* then *erode* of the given field(e.g. remove flame front discontinuities)

        :param passes: [**optional**] number of smoothing iterations
        :type passes: int

        :returns: morphed field over nodes
        """
        # print(morphing_type)
        for _ in range(passes):
            if morphing_type == "open":
                field = self.base_morph(
                    self.base_morph(field, morphing_type="erode"),
                    morphing_type="dilate",
                )
            elif morphing_type == "close":
                field = self.base_morph(
                    self.base_morph(field, morphing_type="dilate"),
                    morphing_type="erode",
                )
            elif morphing_type in ['dilate', 'erode']: #== ("dilate" or "erode"):
                field = self.base_morph(field, morphing_type=morphing_type)
            else:
                msg = (
                    "Morphing type must be one of 'dilate', 'erode', 'open' or 'close'"
                )
                raise ValueError(msg)

        return field

    def approx_gradmag(self, field, edge):
        """method to compute approximative maximum gradient on each node

        :param field: field to be morphed (node centered)
        :param edge: edges approximation (use the approx_edge_from_vol_node tool if needed)

        :returns: maximum gradient field over nodes
        """
        cells = self._tet2nde.repeat(4, axis=1).reshape((-1, 4, 4))
        maxima = np.divide(
            np.abs(field[cells.transpose((0, 2, 1))] - field[cells]), edge[cells]
        ).max(axis=1)
        sorted_idx = np.argsort(maxima - field[self._tet2nde], 0)
        field[
            np.take_along_axis(self._tet2nde, sorted_idx, axis=0)
        ] = np.take_along_axis(maxima, sorted_idx, axis=0)

        return field

    def get_scatter(self):
        """get the scattered field function

        :param self: uses the builtin parameters gather matrix and bincount if instanciated

        :returns: a method to scatter values over nodes
        """

        def scatter(cells):
            tmp = self.gather_matrix.T * cells
            return tmp / self._bincount

        return scatter

    def base_morph(self, values_vtx, morphing_type="dilate"):
        """function to remorph values over given operation and morphing type

        :param values_vtx: input field over nodes
        :param morphing_type: [**optional**] basic morphing: either **dilate** or **erode**

        :returns: morphed field over nodes
        """
        fld_out = np.zeros(values_vtx.shape)

        if self._ope == "smooth":
            # recovering scatter function
            scat = self.get_scatter()
            # gather scatter values : smooth
            fld_out = scat(self.gather_matrix * values_vtx) / self._elt
        else:
            # building remorph direction
            if morphing_type == "dilate":
                # computing maximum by cell (gather)
                val_cell = values_vtx[self._tet2nde].max(axis=1)
                # retrieving cell order (from min to max)
                sorted_idx = np.argsort(val_cell)
                # computing max values of each cell
                vals = val_cell[sorted_idx].repeat(4).reshape((-1, 4))
                # remorphing: broadcast the values of the cells to the nodes composing it (scatter)
                fld_out[self._tet2nde[sorted_idx, :]] = vals
            elif morphing_type == "erode":
                # computing minimum by cell
                val_cell = values_vtx[self._tet2nde].min(axis=1)
                # retrieving cell order (from max to min)
                sorted_idx = np.flip(np.argsort(val_cell))
                # computing max values of each cell
                vals = val_cell[sorted_idx].repeat(4).reshape((-1, 4))
                # remorphing: broadcast the values of the cells to the nodes composing it
                fld_out[self._tet2nde[sorted_idx, :]] = vals
            else:
                raise ValueError("Morphing type must be either 'dilate' or 'erode'")

        return fld_out


def approx_vol_node_from_vol_cell(vol_cell):
    """Function to approximate volume at node from cell volume

    :param vol_cell: cell volume to be converte into node volume (multiplication by 4.5)

    :returns: node volume
    """
    return vol_cell * 4.5


def approx_vol_cell_from_vol_node(vol_node):
    """Function to approximate cell volume from volume at node

    :param vol_node: node volume to be converte into cell volume (division by 4.5)

    :returns: cell volume
    """
    return vol_node / 4.5


def approx_vol_node_from_edge(edge):
    r"""Function to approximate volume at node from edge size

    .. math:: V_{node} = (e^3 \frac{\sqrt(2)}{12}) * 4.5

    :param edge: edge size to be computed into a node volume equivalent

    :returns: node volume
    """
    return approx_vol_node_from_vol_cell(np.power(edge, 3) * np.sqrt(2.0) / 12.0)


def approx_edge_from_vol_node(vol_node):
    r"""Function to approximate edge size from volume at node

    .. math:: e = (\frac{V_{node}}{4.5} \frac{12}{\sqrt(2)})^{1/3}

    :param vol_node: node volume to be computed into an edge size equivalent

    :returns: edge size
    """
    return np.power(
        approx_vol_cell_from_vol_node(vol_node) * 12.0 / np.sqrt(2.0), 1.0 / 3.0
    )



#------------------------------------#
#------------------------------------#
# The following set of functions have been ported from hdfdict 0.1.1
# taking into account the changes (unpack dataset) present in hdfdict 0.3.1
# which ensures compatability of tekigo with python 3.6

TYPEID = '_type_'

def _check_hdf_file(hdf):
    """Returns h5py File if hdf is string (needs to be a path)."""
    if isinstance(hdf, str):
        hdf = h5py.File(hdf)
    return hdf

def unpack_dataset(item):
    """Reconstruct a hdfdict dataset.
    Only some special unpacking for yaml and datetime types.

    Parameters
    ----------
    item : h5py.Dataset

    Returns
    -------
    value : Unpacked Data
    
    """
    value = item[()]
    if TYPEID in item.attrs:
        if item.attrs[TYPEID].astype(str) == 'datetime':
            if hasattr(value, '__iter__'):
                value = [datetime.fromtimestamp(
                    ts) for ts in value]
            else:
                value = datetime.fromtimestamp(value)

        if item.attrs[TYPEID].astype(str) == 'yaml':
            value = yaml.safe_load(value.decode())
    return value

def load_local(hdf):
    """Returns a dictionary containing the
    groups as keys and the datasets as values
    from given hdf file.

    NOTE: This is a copy paste of load() from hdfdict 0.1.1 with
            addition of the unpack_dataset function call.

    Parameters
    ----------
    hdf : string (path to file) or `h5py.File()` or `h5py.Group()`

    Returns
    -------
    d : dict
        The dictionary containing all groupnames as keys and
        datasets as values.
    """
    hdf = _check_hdf_file(hdf)
    d = {}

    def _recurse(h, d):
        for k, v in h.items():
            # print(type(v))
            # print(isinstance(v, h5py.Group))
            # print(isinstance(v, h5py.Dataset))
            if isinstance(v, h5py.Group):
                d[k] = {}
                d[k] = _recurse(v, d[k])
            elif isinstance(v, h5py.Dataset):
                d[k] = unpack_dataset(v)     
                # d[k] = v.value  -> original code
        return d

    return _recurse(hdf, d)