from typing import Any, List, Dict, Tuple, Optional

import drb
import netCDF4 as netCDF

from drb import DrbNode
from drb.exceptions import DrbNotImplementationException, DrbException

from drb_impl_netcdf.netcdf_common import DrbNetcdfAbstractNode


class DrbNetcdfGroupNode(DrbNetcdfAbstractNode):

    supported_impl = {
        netCDF.Dataset
    }

    def __init__(self, parent: DrbNode, data_set: netCDF.Dataset):
        name = data_set.name
        if name == '/':
            name = 'root'
        self._name = name
        self._attributes: Dict[Tuple[str, str], Any] = None
        self._parent: DrbNode = parent
        self._children: List[DrbNode] = None
        self._path = None
        self._data_set = data_set

    @property
    def parent(self) -> Optional[DrbNode]:
        return self._parent

    @property
    def name(self) -> str:
        return self._name

    @property
    def value(self) -> Optional[Any]:
        return None

    @property
    def attributes(self) -> Dict[Tuple[str, str], Any]:
        if self._attributes is None:
            self._attributes = {}
            for attribute_name in self._data_set.ncattrs():
                self._attributes[(attribute_name, None)] = \
                    getattr(self._data_set, attribute_name)

        return self._attributes

    def get_attribute(self, name: str, namespace_uri: str = None) -> Any:
        key = (name, namespace_uri)
        if key in self.attributes.keys():
            return self.attributes[key]
        raise DrbException(f'Attribute not found name: {name}, '
                           f'namespace: {namespace_uri}')

    @property
    @drb.resolve_children
    def children(self) -> List[DrbNode]:
        from drb_impl_netcdf import DrbNetcdfListNode, \
            DrbNetcdfDimensionNode, DrbNetcdfVariableNode

        if self._children is None:
            self._children = []
            dimensions = self._data_set.dimensions
            if dimensions is not None and len(dimensions) > 0:
                nodelist = DrbNetcdfListNode(self, 'dimensions')
                for dim in dimensions:
                    nodelist.append_child(
                        DrbNetcdfDimensionNode(nodelist, dimensions[dim]))
                self._children.append(nodelist)

            variables = self._data_set.variables
            if variables is not None and len(variables) > 0:
                nodelist = DrbNetcdfListNode(self, 'variables')
                for variable in variables:
                    nodelist.append_child(
                        DrbNetcdfVariableNode(nodelist, variables[variable]))
                self._children.append(nodelist)

            groups = self._data_set.groups
            for grp in groups.values():
                self._children.append(DrbNetcdfGroupNode(self, grp))
        return self._children

    def has_child(self) -> bool:
        return len(self.children) > 0

    def has_impl(self, impl: type) -> bool:
        if impl in self.supported_impl:
            return True

    def get_impl(self, impl: type) -> Any:
        if self.has_impl(impl):
            return self._data_set
        raise DrbNotImplementationException(f'no {impl} '
                                            f'implementation found')
