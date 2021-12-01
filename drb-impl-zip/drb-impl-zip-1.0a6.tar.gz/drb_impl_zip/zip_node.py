import enum
import io
import zipfile
from typing import Any, List, Dict, Optional, Tuple

import drb

from drb import DrbNode, AbstractNode
from drb.exceptions import DrbNotImplementationException, DrbException
from drb.path import ParsedPath


class DrbZipAttributeNames(enum.Enum):
    SIZE = 'size'
    DIRECTORY = 'directory'
    RATIO = 'ratio'
    PACKED = 'packed'


class DrbZipNode(AbstractNode):

    supported_impl = {
        io.BufferedIOBase,
        zipfile.ZipExtFile
    }

    def __init__(self, parent: DrbNode, zip_info: zipfile.ZipInfo):
        self._zip_info = zip_info
        self._attributes: Dict[Tuple[str, str], Any] = None
        self._name = None
        self._parent: DrbNode = parent
        self._children: List[DrbNode] = None
        self._path = None

    @property
    def parent(self) -> Optional[DrbNode]:
        return self._parent

    @property
    def path(self) -> ParsedPath:
        if self._path is None:
            self._path = self.parent.path / self.name
        return self._path

    @property
    def name(self) -> str:
        if self._name is None:
            if self._zip_info.filename.endswith('/'):
                self._name = self._zip_info.filename[:-1]
            else:
                self._name = self._zip_info.filename
            if '/' in self._name:
                self._name = self._name[self._name.rindex('/') + 1:]
        return self._name

    @property
    def namespace_uri(self) -> Optional[str]:
        return None

    @property
    def value(self) -> Optional[Any]:
        return None

    @property
    def attributes(self) -> Dict[Tuple[str, str], Any]:
        if self._attributes is None:
            self._attributes = {}
            name_attribute = DrbZipAttributeNames.DIRECTORY.value
            self._attributes[name_attribute, None] = self._zip_info.is_dir()

            name_attribute = DrbZipAttributeNames.SIZE.value
            self._attributes[name_attribute, None] = self._zip_info.file_size

            name_attribute = DrbZipAttributeNames.RATIO.value
            if self._zip_info.compress_size > 0:
                self._attributes[name_attribute, None] = \
                    self._zip_info.file_size / self._zip_info.compress_size
            else:
                self._attributes[name_attribute, None] = 0
            name_attribute = DrbZipAttributeNames.PACKED.value
            self._attributes[name_attribute, None] = \
                self._zip_info.compress_size
        return self._attributes

    def get_attribute(self, name: str, namespace_uri: str = None) -> Any:
        key = (name, namespace_uri)
        if key in self.attributes.keys():
            return self.attributes[key]
        raise DrbException(f'Attribute not found name: {name}, '
                           f'namespace: {namespace_uri}')

    def get_file_list(self):
        return self.parent.get_file_list()

    def _is_a_child(self, filename):
        if not filename.startswith(self._zip_info.filename):
            return False

        filename = filename[len(self._zip_info.filename):]

        if not filename:
            return False

        if not filename.startswith('/') and \
                not self._zip_info.filename.endswith('/'):
            return False

        # Either the name do not contains sep either only one a last position
        return '/' not in filename or filename.index('/') == (
                len(filename) - 1)

    @property
    @drb.resolve_children
    def children(self) -> List[DrbNode]:
        if self._children is None:
            self._children = [DrbZipNode(self, entry) for entry in
                              self.get_file_list()
                              if self._is_a_child(entry.filename)]
            self._children = sorted(self._children,
                                    key=lambda entry_cmp: entry_cmp.name)

        return self._children

    def has_child(self) -> bool:
        return len(self.children) > 0

    def has_impl(self, impl: type) -> bool:
        if impl in self.supported_impl:
            return not self.get_attribute(
                DrbZipAttributeNames.DIRECTORY.value, None)

    def get_impl(self, impl: type) -> Any:
        if self.has_impl(impl):
            return self.parent.open_entry(self._zip_info)
        raise DrbNotImplementationException(f'no {impl} '
                                            f'implementation found')

    def close(self):
        pass

    def open_entry(self, zip_info: zipfile.ZipInfo):
        # open the entry on zip file to return ZipExtFile
        # we back to the first node_file to open is
        return self.parent.open_entry(zip_info)
