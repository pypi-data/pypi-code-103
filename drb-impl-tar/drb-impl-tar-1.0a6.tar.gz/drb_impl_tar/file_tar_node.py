import io
import tarfile
from typing import Any, Dict, Tuple, Optional

from drb import DrbNode
from drb.factory import DrbFactory
from drb.path import ParsedPath
from .execptions import DrbTarNodeException
from .tar_node import DrbTarNode


class DrbFileTarNode(DrbTarNode):

    def __init__(self, base_node: DrbNode):
        super().__init__(parent=base_node.parent, tar_info=None)
        self._all_members = None
        self._tar_file = None
        self.base_node = base_node
        self._tar_file_source = None

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
    def tar_file(self) -> tarfile.TarFile:
        if self._tar_file is None:
            try:
                if self.base_node.has_impl(io.BufferedIOBase):
                    self._tar_file_source = self.base_node \
                        .get_impl(io.BufferedIOBase)
                elif self.base_node.has_impl(io.BytesIO):
                    self._tar_file_source = self.base_node \
                        .get_impl(io.BytesIO)
                if self._tar_file_source is not None:
                    self._tar_file = tarfile.TarFile(fileobj=self
                                                     ._tar_file_source)
                else:
                    raise DrbTarNodeException(
                        f'Unsupported base_node'
                        f' {type(self.base_node).__name__} '
                        f'for DrbFileTarNode')
            except Exception as e:
                raise DrbTarNodeException(f'Unable to read tar file'
                                          f' {self.name} ') from e

        return self._tar_file

    def has_impl(self, impl: type) -> bool:
        return self.base_node.has_impl(impl)

    def get_impl(self, impl: type) -> Any:
        return self.base_node.get_impl(impl)

    def get_members(self):
        if self._all_members is None:
            self._all_members = self.tar_file.getmembers()
        return self._all_members

    def _is_a_child(self, filename):

        # chek if this entries is a child or a sub child if yes => not a child
        # of the root
        if any(filename.startswith(name_entry) and filename != name_entry
               for name_entry in self.tar_file.getnames()):
            return False
        return True

    def open_member(self, tar_info: tarfile.TarInfo):
        # open a member of the tar en return an BufferedIOBase impl
        return self._tar_file.extractfile(tar_info)

    def close(self):
        if self._tar_file_source is not None:
            self._tar_file_source.close()
        if self._tar_file is not None:
            self._tar_file.close()
        self.base_node.close()


class DrbTarFactory(DrbFactory):

    def _create(self, node: DrbNode) -> DrbNode:
        return DrbFileTarNode(base_node=node)
