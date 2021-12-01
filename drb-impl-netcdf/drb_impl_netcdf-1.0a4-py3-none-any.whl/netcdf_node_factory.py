import io
import tempfile
from typing import Any, List, Dict, Tuple, Optional

import netCDF4

from drb import DrbNode, AbstractNode
from drb.factory import DrbFactory
from drb.path import ParsedPath
from drb_impl_file import DrbFileNode

from drb_impl_netcdf.execptions import DrbNetcdfNodeException
from drb_impl_netcdf.netcdf_group_node import DrbNetcdfGroupNode


class DrbNetcdfNode(AbstractNode):

    def __init__(self, base_node: DrbNode):
        self._netcdf_file_source = None
        self._root_dataset = None
        self.base_node = base_node
        stream_io = None
        if isinstance(self.base_node, DrbFileNode):
            self._netcdf_file_source = self.base_node \
                         .get_impl(io.BufferedIOBase)
        else:
            if self.base_node.has_impl(io.BytesIO):
                stream_io = self.base_node.get_impl(io.BytesIO)
            elif self.base_node.has_impl(io.BufferedIOBase):
                stream_io = self.base_node.get_impl(io.BufferedIOBase)

            if stream_io is not None:
                self._netcdf_file_source = tempfile.NamedTemporaryFile()
                self._netcdf_file_source.write(stream_io.read())
                stream_io.close()
            else:
                raise DrbNetcdfNodeException(f'Unsupported parent '
                                             f'{type(self.base_node).__name__}'
                                             f' for DrbNetcdfRootNode')
        filename = self._netcdf_file_source.name

        self._root_dataset = netCDF4.Dataset(filename=filename)
        self.root_node = DrbNetcdfGroupNode(self, self._root_dataset)

    @property
    def parent(self) -> Optional[DrbNode]:
        return self.base_node.parent

    @property
    def path(self) -> ParsedPath:
        return self.base_node.path

    @property
    def name(self) -> str:
        return self.base_node.name

    @property
    def namespace_uri(self) -> Optional[str]:
        return self.base_node.namespace_uri

    @property
    def value(self) -> Optional[Any]:
        return self.base_node.value

    @property
    def attributes(self) -> Dict[Tuple[str, str], Any]:
        return self.base_node.attributes

    def get_attribute(self, name: str, namespace_uri: str = None) -> Any:
        return self.base_node.get_attribute(name, namespace_uri)

    @property
    def children(self) -> List[DrbNode]:
        return [self.root_node]

    def has_child(self) -> bool:
        return True

    def has_impl(self, impl: type) -> bool:
        return self.base_node.has_impl(impl)

    def get_impl(self, impl: type) -> Any:
        return self.base_node.get_impl(impl)

    def close(self):
        if self._root_dataset is not None:
            self._root_dataset.close()
        if self._netcdf_file_source is not None:
            self._netcdf_file_source.close()
        self.base_node.close()


class DrbNetcdfFactory(DrbFactory):

    def _create(self, node: DrbNode) -> DrbNode:
        return DrbNetcdfNode(base_node=node)
